from typing import Generator, Literal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from app.config import settings


ActiveDB = Literal["hospital", "warehouse"]


class DatabaseManager:
	def __init__(self) -> None:
		self._engines = {
			"hospital": create_engine(settings.hospital_db_url, pool_pre_ping=True, future=True),
			"warehouse": create_engine(settings.warehouse_db_url, pool_pre_ping=True, future=True),
		}
		self._sessions = {
			"hospital": sessionmaker(bind=self._engines["hospital"], autoflush=False, autocommit=False, future=True),
			"warehouse": sessionmaker(bind=self._engines["warehouse"], autoflush=False, autocommit=False, future=True),
		}
		self._active: ActiveDB = "hospital"

	@property
	def active(self) -> ActiveDB:
		return self._active

	def switch(self, target: ActiveDB) -> ActiveDB:
		if target not in ("hospital", "warehouse"):
			raise ValueError("Unsupported target database")
		self._active = target
		return self._active

	@contextmanager
	def session_scope(self) -> Generator[Session, None, None]:
		SessionLocal = self._sessions[self._active]
		session: Session = SessionLocal()
		try:
			yield session
			session.commit()
		except Exception:
			session.rollback()
			raise
		finally:
			session.close()

	def test_connections(self) -> dict:
		"""测试数据库连接"""
		results = {}
		for db_name, engine in self._engines.items():
			try:
				with engine.connect() as conn:
					conn.execute(text("SELECT 1"))
					results[db_name] = {"status": "connected", "error": None}
			except Exception as e:
				results[db_name] = {"status": "failed", "error": str(e)}
		return results


manager = DatabaseManager()


def get_db_session() -> Generator[Session, None, None]:
	with manager.session_scope() as session:
		yield session
