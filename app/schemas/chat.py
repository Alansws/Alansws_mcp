from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict


class ChatRequest(BaseModel):
	user_id: str = Field(..., description="调用者的用户标识")
	role: Optional[str] = Field(default=None, description="调用者角色（可直传或由后端根据 user_id 解析）")
	question: str = Field(..., description="用户自然语言问题")
	model_type: Optional[str] = Field(default="auto", description="模型类型：auto(自动选择), local(本地模型), cloud(云端模型)")
	cloud_model: Optional[str] = Field(default=None, description="指定的云端模型名称")
	enable_cross_db: Optional[bool] = Field(default=False, description="是否启用跨库查询功能")


class ChatResponse(BaseModel):
	answer: str
	meta: Optional[Any] = None


class CrossDBRequest(BaseModel):
	user_id: str = Field(..., description="调用者的用户标识")
	role: Optional[str] = Field(default=None, description="调用者角色")
	question: str = Field(..., description="跨库查询的自然语言问题")
	model_type: Optional[str] = Field(default="auto", description="模型类型")
	cloud_model: Optional[str] = Field(default=None, description="指定的云端模型名称")


class ExpertToolResult(BaseModel):
	tool_name: str = Field(..., description="专家工具名称")
	database: str = Field(..., description="查询的数据库")
	query: str = Field(..., description="执行的查询")
	result: Any = Field(..., description="查询结果")
	success: bool = Field(..., description="查询是否成功")
	error_message: Optional[str] = Field(default=None, description="错误信息")


class CrossDBResponse(BaseModel):
	answer: str = Field(..., description="最终的综合答案")
	reasoning: str = Field(..., description="推理过程")
	tool_results: List[ExpertToolResult] = Field(..., description="各专家工具的执行结果")
	meta: Optional[Dict[str, Any]] = Field(default=None, description="元数据信息")
