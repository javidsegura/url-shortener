# database.py - Production-ready database configuration
import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from url_shortener.core.settings.app_settings import app_settings

AsyncSessionLocal = None


def initialize_db_engine():
	global AsyncSessionLocal

	DATABASE_URL = (
			f"{app_settings.MYSQL_ASYNC_DRIVER}"
			f"://{app_settings.MYSQL_USER}:{app_settings.MYSQL_PASSWORD}@{app_settings.MYSQL_HOST}"
			f":{app_settings.MYSQL_PORT}/{app_settings.MYSQL_DATABASE}"
		)



	# Production engine configuration
	engine = create_async_engine(
		DATABASE_URL,
		echo=False,  # Never True in production (performance impact)
		pool_size=10,  # Connection pool size
		max_overflow=20,  # Additional connections when pool is full
		pool_pre_ping=True,  # Validate connections before use
		pool_recycle=3600,  # Recycle connections every hour
	)

	AsyncSessionLocal = async_sessionmaker(
		engine, class_=AsyncSession, expire_on_commit=False
	)

