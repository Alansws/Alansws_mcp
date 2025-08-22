"""
跨库专家工具模块
实现专门查询特定数据库的专家工具
"""

from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.manager import manager
from app.llm.local_client import local_client
from app.llm.cloud_client import cloud_client
from app.schemas.chat import ExpertToolResult


class BaseExpertTool:
    """专家工具基类"""
    
    def __init__(self, database_name: str, table_schema: str):
        self.database_name = database_name
        self.table_schema = table_schema
        self.tool_name = f"{database_name}_Expert"
    
    def _generate_sql(self, question: str, model_type: str = "auto", cloud_model: str = None) -> str:
        """生成SQL查询语句"""
        prompt = f"""你是一个专业的SQL生成助手，专门负责查询{self.database_name}数据库。

数据库表结构：
{self.table_schema}

用户问题：{question}

请根据问题生成准确的SQL查询语句。只返回SQL语句，不要包含任何解释文字。

SQL:"""
        
        try:
            if model_type == "local" or model_type == "auto":
                if local_client.is_available():
                    return local_client.generate_sql(question, self.table_schema)
                elif model_type == "local":
                    raise RuntimeError("本地模型不可用")
            
            # 使用云端模型
            messages = [
                {"role": "system", "content": f"你是一个专业的SQL生成助手，专门负责查询{self.database_name}数据库。请严格遵循以下规则：1. 只返回SQL语句，不要任何解释文字；2. 确保SQL语法完全正确；3. 只查询{self.database_name}数据库中的表。"},
                {"role": "user", "content": prompt}
            ]
            
            response = cloud_client.chat_completion(messages, cloud_model)
            return self._clean_sql_response(response)
            
        except Exception as e:
            # 返回一个安全的默认查询
            return f"SELECT NULL AS result FROM {self.database_name}.dummy_table WHERE 1=0"
    
    def _clean_sql_response(self, response: str) -> str:
        """清理SQL响应"""
        cleaned = response.strip()
        
        # 移除markdown标记
        if cleaned.startswith('```sql'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        # 查找第一个SQL关键字
        sql_keywords = ['SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP']
        sql_start = -1
        
        for keyword in sql_keywords:
            pos = cleaned.upper().find(keyword)
            if pos != -1 and (sql_start == -1 or pos < sql_start):
                sql_start = pos
        
        if sql_start != -1:
            cleaned = cleaned[sql_start:]
            
            # 查找SQL语句的结束位置
            if ';' in cleaned:
                cleaned = cleaned[:cleaned.find(';') + 1]
            else:
                cleaned = cleaned.rstrip() + ';'
        
        return cleaned.strip()
    
    def _execute_query(self, sql: str, db_session: Session) -> Any:
        """执行SQL查询"""
        try:
            result = db_session.execute(text(sql))
            rows = result.fetchall()
            
            if rows:
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
            else:
                return []
                
        except Exception as e:
            raise RuntimeError(f"SQL执行失败: {str(e)}")
    
    def _format_result(self, question: str, result: Any, model_type: str = "auto", cloud_model: str = None) -> str:
        """格式化查询结果"""
        if not result:
            return f"在{self.database_name}数据库中没有找到相关信息。"
        
        try:
            if model_type == "local" or model_type == "auto":
                if local_client.is_available():
                    return local_client.format_answer(question, str(result))
                elif model_type == "local":
                    raise RuntimeError("本地模型不可用")
            
            # 使用云端模型
            prompt = f"""你是一个专业的数据分析师。请根据用户的原始问题和查询结果，生成一个清晰、易懂的自然语言答案。

用户问题：{question}

查询结果：{result}

请生成一个简洁、专业的答案，直接回答用户的问题。用中文回答。

答案："""
            
            messages = [
                {"role": "system", "content": "你是一个专业的数据分析师，请用中文回答。"},
                {"role": "user", "content": prompt}
            ]
            
            return cloud_client.chat_completion(messages, cloud_model)
            
        except Exception as e:
            # 返回简单的格式化结果
            return f"查询到 {len(result)} 条记录：{result}"


class HospitalExpertTool(BaseExpertTool):
    """医疗数据库专家工具"""
    
    def __init__(self):
        table_schema = """
医疗数据库 (hospital_db) 表结构：

1. doctors (医生信息表)
   - doctor_id: VARCHAR(10) - 医生ID (主键)
   - doctor_name: VARCHAR(50) - 医生姓名
   - department: VARCHAR(50) - 所属科室
   - title: VARCHAR(50) - 职称/角色

2. patients (病人信息表)
   - patient_id: VARCHAR(10) - 病人ID (主键)
   - patient_name: VARCHAR(50) - 病人姓名
   - gender: VARCHAR(10) - 性别
   - birth_date: DATE - 出生日期
   - contact_number: VARCHAR(20) - 联系电话
   - primary_doctor_id: VARCHAR(10) - 主治医生ID (外键关联doctors.doctor_id)

3. medical_records (诊疗记录表)
   - record_id: INT - 记录ID (主键，自增)
   - patient_id: VARCHAR(10) - 病人ID (外键关联patients.patient_id)
   - doctor_id: VARCHAR(10) - 看诊医生ID (外键关联doctors.doctor_id)
   - visit_date: DATETIME - 就诊日期
   - diagnosis: TEXT - 诊断结果
   - prescription: TEXT - 处方
"""
        super().__init__("hospital_db", table_schema)
    
    def query(self, question: str, db_session: Session, model_type: str = "auto", cloud_model: str = None) -> ExpertToolResult:
        """执行医疗数据库查询"""
        try:
            # 1. 生成SQL
            sql = self._generate_sql(question, model_type, cloud_model)
            
            # 2. 执行查询
            result = self._execute_query(sql, db_session)
            
            # 3. 格式化结果
            formatted_result = self._format_result(question, result, model_type, cloud_model)
            
            return ExpertToolResult(
                tool_name=self.tool_name,
                database=self.database_name,
                query=sql,
                result=formatted_result,
                success=True
            )
            
        except Exception as e:
            return ExpertToolResult(
                tool_name=self.tool_name,
                database=self.database_name,
                query="",
                result="",
                success=False,
                error_message=str(e)
            )


class WarehouseExpertTool(BaseExpertTool):
    """仓储数据库专家工具"""
    
    def __init__(self):
        table_schema = """
仓储数据库 (warehouse_db) 表结构：

1. warehouse_staff (仓库员工表)
   - staff_id: VARCHAR(10) - 员工ID (主键)
   - staff_name: VARCHAR(50) - 员工姓名
   - role: VARCHAR(50) - 角色/岗位 (Manager/Operator)

2. products (商品信息表)
   - product_id: VARCHAR(10) - 商品ID (主键)
   - product_name: VARCHAR(100) - 商品名称
   - description: TEXT - 商品描述
   - price: DECIMAL(10,2) - 单价
   - supplier: VARCHAR(100) - 供应商

3. inventory (库存表)
   - inventory_id: INT - 库存记录ID (主键，自增)
   - product_id: VARCHAR(10) - 商品ID (外键关联products.product_id)
   - warehouse_location: VARCHAR(20) - 仓库位置
   - quantity: INT - 库存数量
   - last_updated: TIMESTAMP - 最后更新时间

4. shipments (出入库记录表)
   - shipment_id: INT - 记录ID (主键，自增)
   - product_id: VARCHAR(10) - 商品ID (外键关联products.product_id)
   - staff_id: VARCHAR(10) - 操作员工ID (外键关联warehouse_staff.staff_id)
   - quantity_change: INT - 数量变化 (正数入库, 负数出库)
   - record_time: DATETIME - 记录时间
   - type: VARCHAR(20) - 类型 (INBOUND/OUTBOUND)
"""
        super().__init__("warehouse_db", table_schema)
    
    def query(self, question: str, db_session: Session, model_type: str = "auto", cloud_model: str = None) -> ExpertToolResult:
        """执行仓储数据库查询"""
        try:
            # 1. 生成SQL
            sql = self._generate_sql(question, model_type, cloud_model)
            
            # 2. 执行查询
            result = self._execute_query(sql, db_session)
            
            # 3. 格式化结果
            formatted_result = self._format_result(question, result, model_type, cloud_model)
            
            return ExpertToolResult(
                tool_name=self.tool_name,
                database=self.database_name,
                query=sql,
                result=formatted_result,
                success=True
            )
            
        except Exception as e:
            return ExpertToolResult(
                tool_name=self.tool_name,
                database=self.database_name,
                query="",
                result="",
                success=False,
                error_message=str(e)
            )
