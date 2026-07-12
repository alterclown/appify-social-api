import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import the centralized async database engine
from app.configs.database import engine

# Import your routers
from app.routers.auth_router import router as auth_router
from app.routers.feed_router import router as feed_router
from app.routers.comments_router import router as comments_router

# ==============================================================================
# 🚀 LIFESPAN MANAGEMENT
# ==============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown lifecycle tasks.
    """
    # Startup actions go here (if any)
    yield
    # Shutdown: Clean up resource footprints and close connection threads cleanly
    await engine.dispose()
    print("🛑 Database engine connection pool disposed safely.")


# ==============================================================================
# ⚙️ FASTAPI ENGINE INITIALIZATION
# ==============================================================================
app = FastAPI(
    title="NexusNMS Schema API",
    description="API endpoints corresponding to the learned database schemas.",
    version="1.0.0",
    lifespan=lifespan
)


# ==============================================================================
# 🔓 CORS MIDDLEWARE
# ==============================================================================
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==============================================================================
# 🗺️ ROUTER REGISTRATION
# ==============================================================================
app.include_router(auth_router)
app.include_router(feed_router)
app.include_router(comments_router)