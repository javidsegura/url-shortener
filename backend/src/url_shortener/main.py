from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
 
from url_shortener.core.clients.firebase import initialize_firebase
from url_shortener.routers import (
	health_router,
	link_router,
	redirect_router,
	user_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager to handle application startup and shutdown events.
    This is the recommended way to manage resources that need to be
    available for the entire application lifecycle.
    """
    initialize_firebase()

    yield

    # --- Shutdown ---
    # You can add any cleanup code here, like closing database connections.
    print("INFO:     Application shutdown complete.")

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
