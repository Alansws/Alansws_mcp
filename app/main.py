from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.api.routes import router as api_router
from app.db.manager import get_db_session, manager
from app.schemas.chat import ChatRequest, ChatResponse
from app.llm.router import router as model_router
from app.llm.local_client import local_client
from app.llm.cloud_client import cloud_client
from app.security.rbac import check_sql_permission, get_user_role_by_id
from app.tools.weather import fetch_weather


app = FastAPI(title="MCP 智能化问答应用", default_response_class=ORJSONResponse)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(api_router, prefix="/api")


@app.get("/")
async def read_index():
    """返回主页"""
    return FileResponse("static/index.html")


@app.get("/api/models/status")
async def get_models_status():
    """获取所有模型的状态"""
    return {
        "local_model": local_client.get_model_info(),
        "cloud_model": {
            "current": cloud_client.get_current_model(),
            "available": cloud_client.get_available_models(),
            "status": "available"  # API易模型通常总是可用的
        }
    }


@app.post("/api/models/switch")
async def switch_model(model_type: str = None, model_name: str = None):
    """切换模型类型或具体的云端模型"""
    if model_type == "local":
        # 尝试重新加载本地模型
        success = local_client.reload_model()
        return {
            "success": success,
            "model_type": "local",
            "status": local_client.get_model_info()
        }
    elif model_type == "cloud":
        # 切换到指定的云端模型
        if model_name and cloud_client.set_model(model_name):
            return {
                "success": True,
                "model_type": "cloud",
                "current_model": cloud_client.get_current_model(),
                "available_models": cloud_client.get_available_models()
            }
        else:
            raise HTTPException(status_code=400, detail=f"无效的云端模型: {model_name}")
    else:
        raise HTTPException(status_code=400, detail="无效的模型类型，支持: local, cloud")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, db: Session = Depends(get_db_session)) -> ChatResponse:
	"""智能问答主接口"""
	try:
		# 1. 获取用户角色
		active_db = manager.active
		user_role = payload.role or get_user_role_by_id(payload.user_id, active_db)
		
		# 2. 意图识别和路由
		query_path = model_router.decide(payload.question)
		
		# 3. 根据路径处理
		if query_path == "text_to_sql":
			return await _handle_database_query(payload, user_role, active_db, db)
		elif query_path == "tool_weather":
			return await _handle_weather_query(payload)
		else:  # general_qa
			return await _handle_general_qa(payload)
			
	except Exception as e:
		raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


async def _handle_database_query(
	payload: ChatRequest, 
	user_role: str, 
	db_type: str, 
	db: Session
) -> ChatResponse:
	"""处理数据库查询"""
	try:
		# 1. 检查是否需要切换数据库
		suggested_db = model_router.suggest_database(payload.question)
		if suggested_db != "unknown" and suggested_db != db_type:
			# 建议切换到其他数据库
			return ChatResponse(
				answer=f"您的问题与当前数据库不匹配。建议切换到{suggested_db == 'warehouse' and '仓储' or '医疗'}数据库来查询相关信息。\n\n当前数据库：{db_type == 'warehouse' and '仓储' or '医疗'}数据库\n建议数据库：{suggested_db == 'warehouse' and '仓储' or '医疗'}数据库\n\n请在左侧面板切换数据库后重新提问。",
				meta={
					"suggestion": f"switch_to_{suggested_db}",
					"current_db": db_type,
					"suggested_db": suggested_db,
					"role": user_role
				}
			)
		
		# 2. 获取表结构
		table_schema = model_router.get_table_schema()
		
		# 3. 生成 SQL（根据用户选择或自动选择模型）
		sql_query = None
		model_used = "unknown"
		
		# 根据用户选择决定使用哪个模型
		if payload.model_type == "local":
			# 强制使用本地模型
			if local_client.is_available():
				sql_query = local_client.generate_sql(payload.question, table_schema)
				model_used = "local_gguf"
			else:
				raise RuntimeError(f"本地模型不可用: {local_client.get_error_message()}")
		elif payload.model_type == "cloud":
			# 强制使用云端模型
			sql_query = await _generate_sql_with_cloud(payload.question, table_schema, payload.cloud_model)
			model_used = "cloud_api"
		else:
			# 自动选择：优先使用本地模型，失败时降级到云端模型
			try:
				if local_client.is_available():
					sql_query = local_client.generate_sql(payload.question, table_schema)
					model_used = "local_gguf"
				else:
					raise RuntimeError(f"本地模型不可用: {local_client.get_error_message()}")
			except Exception as e:
				# 本地模型失败，使用云端模型
				print(f"本地模型失败，降级到云端模型: {e}")
				sql_query = await _generate_sql_with_cloud(payload.question, table_schema, payload.cloud_model)
				model_used = "cloud_api"
		
		# 3. 权限校验
		has_permission, permission_msg = check_sql_permission(sql_query, user_role)
		if not has_permission:
			return ChatResponse(
				answer=f"权限不足：{permission_msg}",
				meta={"sql": sql_query, "role": user_role, "permission": False, "model": model_used}
			)
		
		# 4. 执行查询
		result = db.execute(text(sql_query))
		rows = result.fetchall()
		
		# 5. 格式化结果
		if rows:
			# 转换为字典列表
			columns = result.keys()
			data = [dict(zip(columns, row)) for row in rows]
			formatted_result = f"查询到 {len(rows)} 条记录：{data}"
		else:
			formatted_result = "查询结果为空"
		
		# 6. 生成自然语言答案（根据用户选择或自动选择模型）
		if payload.model_type == "local":
			# 强制使用本地模型
			if local_client.is_available():
				answer = local_client.format_answer(payload.question, formatted_result)
				answer_model = "local_gguf"
			else:
				raise RuntimeError(f"本地模型不可用: {local_client.get_error_message()}")
		elif payload.model_type == "cloud":
			# 强制使用云端模型
			answer = await _format_answer_with_cloud(payload.question, formatted_result, payload.cloud_model)
			answer_model = "cloud_api"
		else:
			# 自动选择：优先使用本地模型，失败时降级到云端模型
			try:
				if local_client.is_available():
					answer = local_client.format_answer(payload.question, formatted_result)
					answer_model = "local_gguf"
				else:
					raise RuntimeError(f"本地模型不可用: {local_client.get_error_message()}")
			except Exception as e:
				# 本地模型失败，使用云端模型
				print(f"本地模型格式化失败，降级到云端模型: {e}")
				answer = await _format_answer_with_cloud(payload.question, formatted_result, payload.cloud_model)
				answer_model = "cloud_api"
		
		return ChatResponse(
			answer=answer,
			meta={
				"sql": sql_query,
				"role": user_role,
				"permission": True,
				"result_count": len(rows),
				"database": db_type,
				"sql_model": model_used,
				"answer_model": answer_model
			}
		)
		
	except Exception as e:
		return ChatResponse(
			answer=f"数据库查询失败: {str(e)}",
			meta={"error": str(e), "role": user_role}
		)


async def _generate_sql_with_cloud(question: str, table_schema: str, model: str = None) -> str:
	"""使用云端模型生成 SQL"""
	prompt = f"""你是一个专业的 SQL 生成助手。根据用户的问题和数据库表结构，生成准确的 SQL 查询语句。

数据库表结构：
{table_schema}

用户问题：{question}

重要：请只返回 SQL 语句，不要包含任何解释、注释或其他文字。如果问题与数据库表结构不符，请返回一个语法正确但返回空结果的查询。

SQL:"""
	
	messages = [
		{"role": "system", "content": "你是一个专业的 SQL 生成助手。你的任务是根据用户问题和数据库表结构生成SQL语句。请严格遵循以下规则：1. 只返回SQL语句，不要任何解释文字；2. 如果问题与表结构不符，返回语法正确但返回空结果的查询；3. 不要使用markdown格式；4. 确保SQL语法完全正确。"},
		{"role": "user", "content": prompt}
	]
	
	response = cloud_client.chat_completion(messages, model)
	
	# 改进的SQL清理逻辑
	cleaned_response = response.strip()
	
	# 移除markdown标记
	if cleaned_response.startswith('```sql'):
		cleaned_response = cleaned_response[7:]
	elif cleaned_response.startswith('```'):
		cleaned_response = cleaned_response[3:]
	
	if cleaned_response.endswith('```'):
		cleaned_response = cleaned_response[:-3]
	
	# 移除可能的解释文字（查找第一个SQL关键字）
	sql_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
	cleaned_response = cleaned_response.strip()
	
	# 查找最后一个完整的SQL语句
	# 通常SQL语句以分号结尾，或者以LIMIT、ORDER BY等结尾
	sql_end_markers = [';', 'LIMIT', 'ORDER BY', 'GROUP BY', 'HAVING', 'UNION', 'EXCEPT', 'INTERSECT']
	
	# 查找第一个SQL关键字的位置
	sql_start = -1
	for keyword in sql_keywords:
		pos = cleaned_response.upper().find(keyword)
		if pos != -1 and (sql_start == -1 or pos < sql_start):
			sql_start = pos
	
	if sql_start != -1:
		cleaned_response = cleaned_response[sql_start:]
		
		# 查找SQL语句的结束位置
		sql_end = len(cleaned_response)
		for marker in sql_end_markers:
			pos = cleaned_response.upper().find(marker)
			if pos != -1:
				# 找到标记后，查找下一个可能的结束位置
				next_pos = pos + len(marker)
				# 如果后面还有内容，尝试找到分号
				semicolon_pos = cleaned_response.find(';', next_pos)
				if semicolon_pos != -1:
					sql_end = semicolon_pos + 1
					break
				else:
					sql_end = next_pos
					break
		
		cleaned_response = cleaned_response[:sql_end]
	else:
		# 如果没有找到SQL关键字，返回一个安全的默认查询
		if '库存' in question or '数量' in question:
			cleaned_response = "SELECT NULL AS result WHERE 1=0"
		else:
			cleaned_response = "SELECT NULL AS result WHERE 1=0"
	
	# 最终清理：移除多余的空行和解释文字
	lines = cleaned_response.split('\n')
	cleaned_lines = []
	for line in lines:
		line = line.strip()
		# 只保留看起来像SQL的行
		if (line and 
			not line.startswith('--') and 
			not line.startswith('/*') and
			not line.startswith('//') and
			not line.startswith('#') and
			not line.startswith('-') and  # 移除以破折号开头的行
			len(line) > 0):
			cleaned_lines.append(line)
	
	cleaned_response = ' '.join(cleaned_lines)
	
	# 进一步清理：移除SQL语句中的破折号和多余空格
	cleaned_response = cleaned_response.replace(' - ', ' ')
	cleaned_response = cleaned_response.replace('- ', '')
	cleaned_response = cleaned_response.replace(' -', '')
	
	# 移除多余的空格
	import re
	cleaned_response = re.sub(r'\s+', ' ', cleaned_response)
	
	# 更严格的SQL清理：只保留SQL语句部分
	# 查找第一个完整的SQL语句（以SELECT等开头，以分号结尾）
	sql_pattern = r'(SELECT\s+.*?;)'  # 匹配从SELECT开始到分号结束的内容
	match = re.search(sql_pattern, cleaned_response, re.IGNORECASE | re.DOTALL)
	if match:
		cleaned_response = match.group(1)
	
	# 如果仍然包含中文解释文字，尝试更精确的提取
	if '但是' in cleaned_response or '这里' in cleaned_response or '问题' in cleaned_response:
		# 查找最后一个分号的位置
		last_semicolon = cleaned_response.rfind(';')
		if last_semicolon != -1:
			cleaned_response = cleaned_response[:last_semicolon + 1]
	
	# 确保SQL语句以分号结尾
	if not cleaned_response.endswith(';'):
		cleaned_response = cleaned_response.rstrip() + ';'
	
	return cleaned_response.strip()


async def _format_answer_with_cloud(question: str, sql_result: str, model: str = None) -> str:
	"""使用云端模型格式化答案"""
	prompt = f"""你是一个专业的数据分析师。请根据用户的原始问题和 SQL 查询结果，生成一个清晰、易懂的自然语言答案。

用户问题：{question}

查询结果：{sql_result}

请生成一个简洁、专业的答案，直接回答用户的问题。如果结果为空，请说明没有找到相关数据。

答案："""
	
	messages = [
		{"role": "system", "content": "聊天记录中，请用中文回答。"},
		{"role": "user", "content": prompt}
	]
	
	return cloud_client.chat_completion(messages, model)


async def _handle_weather_query(payload: ChatRequest) -> ChatResponse:
	"""处理天气查询"""
	try:
		# 1. 获取天气数据
		weather_data = await fetch_weather("北京")  # 默认北京，可扩展地理编码
		
		# 2. 使用云端模型分析天气数据
		answer = cloud_client.weather_analysis(weather_data, payload.question, payload.cloud_model)
		
		return ChatResponse(
			answer=answer,
			meta={"tool": "weather", "data_source": "open-meteo", "model": payload.cloud_model or "default"}
		)
		
	except Exception as e:
		return ChatResponse(
			answer=f"天气查询失败: {str(e)}",
			meta={"error": str(e)}
		)


async def _handle_general_qa(payload: ChatRequest) -> ChatResponse:
	"""处理通用知识问答"""
	try:
		answer = cloud_client.general_qa(payload.question, payload.cloud_model)
		
		return ChatResponse(
			answer=answer,
			meta={"model": "api易", "type": "general_qa", "specific_model": payload.cloud_model or "default"}
		)
		
	except Exception as e:
		return ChatResponse(
			answer=f"通用问答失败: {str(e)}",
			meta={"error": str(e)}
		)
