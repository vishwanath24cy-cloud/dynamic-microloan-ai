from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db, check_db_connection, SessionLocal
from app.seed import seed_demo_data
from app.routers import borrowers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure SQLite database, tables, and demo seed data are initialized
    init_db()
    db = SessionLocal()
    try:
        seed_demo_data(db)
    finally:
        db.close()
    yield
    # Shutdown: Clean up resources if needed


app = FastAPI(
    title="AI-Based Dynamic Microloan Repayment & Cash-Flow Planner API",
    description="Backend service providing borrower cash-flow analysis, dynamic repayment schedules, and risk prediction.",
    version="0.2.0",
    lifespan=lifespan,
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(borrowers.router)


@app.get("/")
def read_root():
    return {
        "project": "AI-Based Dynamic Microloan Repayment & Cash-Flow Planner",
        "version": "0.2.0",
        "status": "online",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "borrowers": "/api/borrowers",
            "dashboard_summary": "/api/dashboard/summary",
        },
    }


@app.get("/health")
def health_check():
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "dynamic-microloan-ai-backend",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
