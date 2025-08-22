from typing import Optional, Dict, Any
import httpx
from app.config import settings


async def fetch_weather(city: str) -> Dict[str, Any]:
	# 这里可按需替换为实际需要 API；目前示例采用 open-meteo 免鉴权
	params = {
		"latitude": 39.9042,  # 北京示例，可通过地理编码扩展
		"longitude": 116.4074,
		"current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
	}
	async with httpx.AsyncClient(timeout=15) as client:
		resp = await client.get(settings.weather_api_base, params=params)
		resp.raise_for_status()
		return resp.json()
