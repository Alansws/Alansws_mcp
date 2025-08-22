from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
	app_env: str = Field(default="dev")
	app_host: str = Field(default="0.0.0.0")
	app_port: int = Field(default=8000)

	# Databases - 连接到本机 MySQL
	hospital_db_url: str = Field(default="mysql+pymysql://root:0309@127.0.0.1:3306/hospital_db", alias="HOSPITAL_DB_URL")
	warehouse_db_url: str = Field(default="mysql+pymysql://root:0309@127.0.0.1:3306/warehouse_db", alias="WAREHOUSE_DB_URL")

	# Local LLM (GGUF Model)
	gguf_model_path: str = Field(default="/Users/sws/DB-GPT/qwen2-1_5b-instruct-q4_k_m.gguf", alias="GGUF_MODEL_PATH")
	ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
	ollama_model: str = Field(default="llama3", alias="OLLAMA_MODEL")

	# Cloud LLM (API易)
	openai_api_key: str = Field(default="sk-k6vOkTY1imUFpvpgDcD5439dCd2545C79e3549A289E518Da", alias="OPENAI_API_KEY")
	openai_base_url: str = Field(default="https://api.apiyi.com/v1", alias="OPENAI_BASE_URL")
	openai_model: str = Field(default="deepseek-r1", alias="OPENAI_MODEL")  # 默认使用 deepseek-r1
	
	# 可用的API易模型列表
	available_api_models: list = Field(default=["deepseek-r1", "deepseek-chat", "gpt-4o-mini"], alias="AVAILABLE_API_MODELS")

	# Weather tool
	weather_api_base: str = Field(default="https://api.open-meteo.com/v1/forecast", alias="WEATHER_API_BASE")
	weather_api_key: Optional[str] = Field(default=None, alias="WEATHER_API_KEY")

	class Config:
		env_file = ".env"
		case_sensitive = False


settings = Settings()
