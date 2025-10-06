from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from url_shortener.core.clients.firebase import initialize_firebase
from url_shortener.core.logger.logger import initialize_logger
import url_shortener.core.clients as clients
import url_shortener.core.settings as settings
from url_shortener.routers import (
	health_router,
	link_router,
	redirect_router,
	user_router,
)
import logging 
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    This is the recommended way to manage resources that need to be
    available for the entire application lifecycle.
    """
    print("IM BEING INITIALIZED!!!!!!!")
    initialize_firebase()
    initialize_logger() 
    settings.app_settings = settings.initialize_settings()
    clients.s3_client = clients.initialize_aws_s3_client()
    clients.secrets_manager_client = clients.initialize_aws_secrets_manager_client()
    clients.redis = clients.initialize_redis_client()

    yield

    # --- Shutdown ---
    # You can add any cleanup code here, like closing database connections.
    logger.debug("INFO:     Application shutdown complete.")

app = FastAPI(title="URL shortener", lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_methods=["*"],
	allow_headers=["*"],
	allow_credentials=True,
)

routers = [health_router, link_router, user_router]

for router in routers:
	app.include_router(router, prefix="/api")
app.include_router(redirect_router)
