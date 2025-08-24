import os
from typing import List, Dict, Any
from app.config import settings

try:
	from llama_cpp import Llama
	LLAMA_AVAILABLE = True
except ImportError:
	LLAMA_AVAILABLE = False


class LocalGGUFClient:
	def __init__(self):
		self.model_path = settings.gguf_model_path
		self.llm = None
		self._model_loaded = False
		self._error_message = ""
		self._init_model()
	
	def _init_model(self):
		"""初始化本地 GGUF 模型"""
		if not LLAMA_AVAILABLE:
			self._error_message = "llama-cpp-python 未安装，本地模型功能不可用"
			print(f"警告: {self._error_message}")
			return
		
		if not os.path.exists(self.model_path):
			self._error_message = f"模型文件不存在: {self.model_path}"
			print(f"警告: {self._error_message}")
			return
		
		# 验证模型文件大小和完整性
		file_size = os.path.getsize(self.model_path)
		if file_size < 100 * 1024 * 1024:  # 小于100MB
			self._error_message = f"模型文件过小，可能损坏: {file_size / (1024*1024):.1f}MB"
			print(f"警告: {self._error_message}")
			return
		
		print(f"模型文件大小: {file_size / (1024*1024):.1f}MB")
		
		try:
			# 使用更稳定的参数配置
			self.llm = Llama(
				model_path=self.model_path,
				n_ctx=2048,  # 减少上下文长度，提高稳定性
				n_threads=2,  # 减少线程数，避免资源冲突
				n_batch=512,  # 添加批处理大小
				verbose=False,
				use_mmap=True,  # 启用内存映射
				use_mlock=False,  # 禁用内存锁定
				seed=-1  # 随机种子
			)
			self._model_loaded = True
			self._error_message = ""
			print(f"成功加载本地模型: {self.model_path}")
		except Exception as e:
			print(f"第一次尝试加载失败: {e}")
			print("尝试使用更保守的参数重新加载...")
			
			try:
				# 使用更保守的参数重试
				self.llm = Llama(
					model_path=self.model_path,
					n_ctx=1024,  # 进一步减少上下文长度
					n_threads=1,  # 单线程
					n_batch=256,  # 减少批处理大小
					verbose=False,
					use_mmap=False,  # 禁用内存映射
					use_mlock=False,
					seed=-1
				)
				self._model_loaded = True
				self._error_message = ""
				print(f"使用保守参数成功加载本地模型: {self.model_path}")
			except Exception as e2:
				self._error_message = f"初始化模型失败: {e2}"
				print(f"警告: {self._error_message}")
				print("本地模型功能不可用，将使用云端模型作为备选")
				self._model_loaded = False
	
	def get_model_info(self) -> Dict[str, Any]:
		"""获取模型信息"""
		return {
			"name": "qwen2-1.5b-instruct (GGUF)",
			"path": self.model_path,
			"status": "loaded" if self._model_loaded else "failed",
			"available": self._model_loaded,
			"error": self._error_message if not self._model_loaded else "",
			"llama_available": LLAMA_AVAILABLE
		}
	
	def reload_model(self) -> bool:
		"""重新加载模型"""
		try:
			if self.llm:
				del self.llm
			self._init_model()
			return self._model_loaded
		except Exception as e:
			self._error_message = f"重新加载模型失败: {e}"
			return False
	
	def generate_sql(self, question: str, table_schema: str) -> str:
		"""生成 SQL 查询"""
		if not self._model_loaded:
			raise RuntimeError(f"本地模型未加载: {self._error_message}")
		
		prompt = f"""你是一个专业的 SQL 生成助手。根据用户的问题和数据库表结构，生成准确的 SQL 查询语句。

数据库表结构：
{table_schema}

用户问题：{question}

重要：请只返回 SQL 语句，不要包含任何解释、注释或其他文字。如果问题与数据库表结构不符，请返回一个语法正确但返回空结果的查询。

SQL:"""
		
		try:
			response = self.llm.create_chat_completion([
				{"role": "user", "content": prompt}
			])
			sql = response['choices'][0]['message']['content'].strip()
			# 清理可能的 markdown 标记
			if sql.startswith('```sql'):
				sql = sql[7:]
			if sql.endswith('```'):
				sql = sql[:-3]
			return sql.strip()
		except Exception as e:
			raise RuntimeError(f"生成 SQL 失败: {e}")
	
	def format_answer(self, question: str, sql_result: str) -> str:
		"""格式化查询结果为自然语言答案"""
		if not self._model_loaded:
			raise RuntimeError(f"本地模型未加载: {self._error_message}")
		
		prompt = f"""你是一个专业的数据分析师。请根据用户的原始问题和 SQL 查询结果，生成一个清晰、易懂的自然语言答案。

用户问题：{question}

查询结果：{sql_result}

请生成一个简洁、专业的答案，直接回答用户的问题。如果结果为空，请说明没有找到相关数据。

答案："""
		
		try:
			response = self.llm.create_chat_completion([
				{"role": "user", "content": prompt}
			])
			return response['choices'][0]['message']['content'].strip()
		except Exception as e:
			# 如果格式化失败，返回原始结果
			return f"查询结果：{sql_result}"
	
	def is_available(self) -> bool:
		"""检查本地模型是否可用"""
		return self._model_loaded
	
	def get_error_message(self) -> str:
		"""获取错误信息"""
		return self._error_message
	
	def check_model_compatibility(self) -> Dict[str, Any]:
		"""检查模型兼容性"""
		compatibility_info = {
			"llama_cpp_version": "unknown",
			"model_file_exists": False,
			"model_file_size": 0,
			"model_file_readable": False,
			"llama_available": LLAMA_AVAILABLE
		}
		
		try:
			import llama_cpp
			compatibility_info["llama_cpp_version"] = llama_cpp.__version__
		except:
			pass
		
		if os.path.exists(self.model_path):
			compatibility_info["model_file_exists"] = True
			compatibility_info["model_file_size"] = os.path.getsize(self.model_path)
			
			# 检查文件是否可读
			try:
				with open(self.model_path, 'rb') as f:
					f.read(1024)  # 读取前1KB
				compatibility_info["model_file_readable"] = True
			except:
				compatibility_info["model_file_readable"] = False
		
		return compatibility_info


# 全局实例
local_client = LocalGGUFClient()
