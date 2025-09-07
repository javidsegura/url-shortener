from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core import redis_client, settings
from .routers import (
	health_router,
	link_router,
	redirect_router,
	test_router,
	user_router,
)

app = FastAPI(title="URL shortener")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
	allow_credentials=True,
)

routers = [health_router, link_router, user_router, test_router]

for router in routers:
	app.include_router(router, prefix="/api")
app.include_router(redirect_router)
