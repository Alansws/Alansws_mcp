from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.db.manager import manager, ActiveDB

router = APIRouter()


@router.get("/health")
async def health() -> dict:
	return {"status": "ok", "active_db": manager.active}


class SwitchDBBody(BaseModel):
	target: ActiveDB = Field(..., description="hospital 或 warehouse")


@router.post("/switch_db")
async def switch_db(body: SwitchDBBody) -> dict:
	active = manager.switch(body.target)
	return {"active_db": active}


@router.get("/test_db_connections")
async def test_db_connections() -> dict:
	"""测试所有数据库连接"""
	return manager.test_connections()
