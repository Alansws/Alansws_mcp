from typing import List, Dict, Any
from openai import OpenAI
from app.config import settings


class APICloudClient:
	def __init__(self):
		self.client = OpenAI(
			api_key=settings.openai_api_key,
			base_url=settings.openai_base_url
		)
		self.model = settings.openai_model
		self.available_models = settings.available_api_models
	
	def set_model(self, model_name: str) -> bool:
		"""设置要使用的模型"""
		if model_name in self.available_models:
			self.model = model_name
			return True
		return False
	
	def get_available_models(self) -> List[str]:
		"""获取可用的模型列表"""
		return self.available_models.copy()
	
	def get_current_model(self) -> str:
		"""获取当前使用的模型"""
		return self.model
	
	def chat_completion(self, messages: List[Dict[str, str]], model: str = None) -> str:
		"""调用 API易 进行对话"""
		try:
			# 如果指定了模型，使用指定模型；否则使用默认模型
			use_model = model if model and model in self.available_models else self.model
			
			response = self.client.chat.completions.create(
				model=use_model,
				messages=messages,
				max_tokens=1000,
				temperature=0.7
			)
			return response.choices[0].message.content.strip()
		except Exception as e:
			raise RuntimeError(f"API易调用失败 (模型: {use_model}): {e}")
	
	def general_qa(self, question: str, model: str = None) -> str:
		"""通用知识问答"""
		messages = [
			{"role": "system", "content": "你是一个专业、友好的AI助手，请用中文回答用户的问题。"},
			{"role": "user", "content": question}
		]
		return self.chat_completion(messages, model)
	
	def weather_analysis(self, weather_data: Dict[str, Any], user_question: str, model: str = None) -> str:
		"""分析天气数据并生成答案"""
		weather_info = f"""
当前天气数据：
- 温度: {weather_data.get('current', {}).get('temperature_2m', 'N/A')}°C
- 湿度: {weather_data.get('current', {}).get('relative_humidity_2m', 'N/A')}%
- 降水: {weather_data.get('current', {}).get('precipitation', 'N/A')}mm
"""
		
		messages = [
			{"role": "system", "content": "你是一个专业的天气分析师，请根据天气数据回答用户的问题。"},
			{"role": "user", "content": f"{user_question}\n\n{weather_info}"}
		]
		return self.chat_completion(messages, model)
	
	def test_connection(self) -> Dict[str, Any]:
		"""测试API连接"""
		try:
			# 尝试调用一个简单的请求来测试连接
			response = self.client.chat.completions.create(
				model=self.model,
				messages=[{"role": "user", "content": "测试"}],
				max_tokens=10
			)
			return {
				"status": "connected",
				"model": self.model,
				"available_models": self.available_models
			}
		except Exception as e:
			return {
				"status": "failed",
				"error": str(e),
				"model": self.model,
				"available_models": self.available_models
			}


# 全局实例
cloud_client = APICloudClient()
