from typing import Literal, Dict, Any
from app.config import settings
from app.db.manager import manager


QueryPath = Literal["text_to_sql", "general_qa", "tool_weather"]


class ModelRouter:
	def __init__(self):
		self._table_schemas = {}
		self._init_table_schemas()
	
	def _init_table_schemas(self):
		"""初始化数据库表结构信息"""
		# 医疗数据库表结构
		hospital_schema = """
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
		
		# 仓储数据库表结构
		warehouse_schema = """
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
		
		self._table_schemas = {
			"hospital": hospital_schema,
			"warehouse": warehouse_schema
		}
	
	def decide(self, question: str) -> QueryPath:
		"""决定查询路径"""
		q = question.lower().strip()
		
		# 医疗数据库关键词
		hospital_keywords = [
			"医生", "病人", "患者", "诊疗", "诊断", "处方", "科室", "职称",
			"doctors", "patients", "medical_records", "department", "title"
		]
		
		# 仓储数据库关键词
		warehouse_keywords = [
			"库存", "商品", "产品", "仓库", "员工", "出入库", "供应商", "价格",
			"products", "inventory", "warehouse_staff", "shipments", "supplier", "price"
		]
		
		# 通用数据库查询关键词
		db_keywords = ["查询", "select", "记录", "信息"]
		
		# 天气查询关键词
		weather_keywords = ["天气", "weather", "温度", "湿度", "降水"]
		
		# 检查是否需要切换数据库
		if any(k in q for k in warehouse_keywords):
			# 仓储相关查询，建议切换到仓储数据库
			return "text_to_sql"
		elif any(k in q for k in hospital_keywords):
			# 医疗相关查询，建议切换到医疗数据库
			return "text_to_sql"
		elif any(k in q for k in db_keywords):
			# 通用查询，使用当前数据库
			return "text_to_sql"
		elif any(k in q for k in weather_keywords):
			return "tool_weather"
		else:
			return "general_qa"
	
	def suggest_database(self, question: str) -> str:
		"""根据问题内容建议合适的数据库"""
		q = question.lower().strip()
		
		# 医疗数据库关键词
		hospital_keywords = [
			"医生", "病人", "患者", "诊疗", "诊断", "处方", "科室", "职称",
			"doctors", "patients", "medical_records", "department", "title"
		]
		
		# 仓储数据库关键词
		warehouse_keywords = [
			"库存", "商品", "产品", "仓库", "员工", "出入库", "供应商", "价格",
			"products", "inventory", "warehouse_staff", "shipments", "supplier", "price"
		]
		
		if any(k in q for k in warehouse_keywords):
			return "warehouse"
		elif any(k in q for k in hospital_keywords):
			return "hospital"
		else:
			return "unknown"  # 无法确定，使用当前数据库
	
	def get_table_schema(self) -> str:
		"""获取当前激活数据库的表结构"""
		active_db = manager.active
		return self._table_schemas.get(active_db, "未知数据库")
	
	def local_model_name(self) -> str:
		return "qwen2-1.5b-instruct (GGUF)"


router = ModelRouter()
