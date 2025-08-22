from typing import Dict, List
import re

# 基于角色的表权限控制
ROLE_TABLE_PERMS: Dict[str, Dict[str, List[str]]] = {
	# 医疗数据库角色
	"doctor": {
		"allow_tables": ["doctors", "patients", "medical_records"],
		"deny_columns": [],
		"description": "医生可以查看病人信息、诊疗记录和医生信息"
	},
	"主任医师": {
		"allow_tables": ["doctors", "patients", "medical_records"],
		"deny_columns": [],
		"description": "主任医师拥有完整权限"
	},
	"副主任医师": {
		"allow_tables": ["doctors", "patients", "medical_records"],
		"deny_columns": [],
		"description": "副主任医师拥有完整权限"
	},
	"主治医师": {
		"allow_tables": ["doctors", "patients", "medical_records"],
		"deny_columns": [],
		"description": "主治医师拥有完整权限"
	},
	"住院医师": {
		"allow_tables": ["doctors", "patients", "medical_records"],
		"deny_columns": [],
		"description": "住院医师拥有完整权限"
	},
	"patient": {
		"allow_tables": ["doctors"],  # 病人只能查看医生信息
		"deny_columns": [],
		"description": "病人只能查看医生基本信息"
	},
	
	# 仓储数据库角色
	"Manager": {
		"allow_tables": ["warehouse_staff", "products", "inventory", "shipments", "locations"],
		"deny_columns": [],
		"description": "仓库经理拥有完整权限"
	},
	"Operator": {
		"allow_tables": ["products", "inventory", "shipments", "locations"],
		"deny_columns": ["price", "cost"],  # 操作员不能查看商品价格和成本
		"description": "仓库操作员可以查看库存和出入库记录，但不能查看价格和成本"
	},
	
	# 通用角色映射
	"admin": {
		"allow_tables": ["*"],  # 管理员可以访问所有表
		"deny_columns": [],
		"description": "系统管理员拥有所有权限"
	},
	"test_user": {
		"allow_tables": ["doctors", "products"],  # 测试用户只能查看基本信息
		"deny_columns": ["price", "cost", "diagnosis"],
		"description": "测试用户拥有有限权限，用于功能测试"
	}
}


def extract_tables(sql: str) -> List[str]:
	"""从 SQL 中提取表名"""
	pattern = r"(?:from|join)\s+([a-zA-Z_][\w]*)"
	return list({m.lower() for m in re.findall(pattern, sql, flags=re.IGNORECASE)})


def contains_denied_columns(sql: str, denied_columns: List[str]) -> bool:
	"""检查是否包含被禁止的列"""
	denied_columns_lower = [c.lower() for c in denied_columns]
	for col in denied_columns_lower:
		if re.search(rf"\b{re.escape(col)}\b", sql, flags=re.IGNORECASE):
			return True
	return False


def check_sql_permission(sql: str, role: str) -> tuple[bool, str]:
	"""检查 SQL 权限"""
	role = role.strip()
	
	# 查找匹配的角色权限
	perms = None
	for role_key, role_perms in ROLE_TABLE_PERMS.items():
		if role_key.lower() == role.lower() or role.lower() in role_key.lower():
			perms = role_perms
			break
	
	if not perms:
		return False, f"未知角色 '{role}'，无权限执行查询。支持的角色：{list(ROLE_TABLE_PERMS.keys())}"
	
	# 检查表权限
	tables = extract_tables(sql)
	allow_tables = perms["allow_tables"]
	
	for table in tables:
		if allow_tables != ["*"] and table not in allow_tables:
			return False, f"角色 '{role}' 无权访问表 '{table}'。允许的表：{allow_tables}"
	
	# 检查列权限
	if contains_denied_columns(sql, perms.get("deny_columns", [])):
		return False, f"角色 '{role}' 试图访问受限列：{perms['deny_columns']}"
	
	return True, f"权限检查通过。{perms.get('description', '')}"


def get_user_role_by_id(user_id: str, db_type: str) -> str:
	"""根据用户ID和数据库类型获取角色"""
	# 这里可以根据实际需求实现用户角色查询
	# 目前返回默认角色用于测试
	
	if db_type == "hospital":
		# 医疗数据库：根据用户ID前缀判断
		if user_id.startswith("D"):
			return "doctor"  # 医生
		elif user_id.startswith("P"):
			return "patient"  # 病人（只读权限）
		else:
			return "admin"
	elif db_type == "warehouse":
		# 仓储数据库：根据用户ID前缀判断
		if user_id == "S1001":
			return "Manager"  # 仓库经理
		elif user_id == "S1002":
			return "Operator"  # 仓库操作员
		elif user_id.startswith("S"):
			return "Operator"  # 其他S开头的都是操作员
		else:
			return "Manager"  # 默认仓库经理权限
	
	# 特殊用户ID处理
	if user_id == "test_user":
		return "test_user"
	
	return "admin"  # 默认管理员权限
