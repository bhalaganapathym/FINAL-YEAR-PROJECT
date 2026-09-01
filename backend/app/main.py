"""
FastAPI Main Application Entry Point.
Initializes middleware, lifecycle handlers, and registers API routers.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.api.routes import router as analytics_router
from app.api.database_routes import router as database_router
from app.database.connection import test_db_connection
from app.utils.logger import logger

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Performs startup health checks and database connection verification.
    """
    logger.info("Starting Persistent AI Data Analyst application...")
    logger.info(f"Connecting to database at {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    db_connected, db_msg, db_latency = test_db_connection()
    if db_connected:
        logger.info(f"Database connection established successfully in {db_latency:.2f}ms")
    else:
        logger.warning(f"Database connection failed on startup: {db_msg}")

    yield

    logger.info("Shutting down Persistent AI Data Analyst application...")


app = FastAPI(
    title="Persistent AI Data Analyst",
    description=(
        "A LangGraph-based multi-agent system for conversational business intelligence. "
        "Translates natural language questions into safe MySQL queries, executes them against relational databases, "
        "produces grounded statistical explanations, renders Plotly visualizations, forecasts time series, "
        "and supports user uploaded databases & spreadsheets."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware for Frontend Access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(analytics_router)
app.include_router(database_router)
