# FinSight Backend Application Entry Point
# FastAPI app factory with CORS, exception handlers, and route registration

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.db.postgres import init_db, drop_db
from backend.app.db.mongo import init_mongo, close_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    init_db()
    init_mongo()
    yield
    # Shutdown
    close_mongo()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Smart Personal Finance & Budgeting Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "app": settings.APP_NAME}


# Include routes (imported at runtime to avoid circular imports)
from backend.app.routes import auth, accounts, transactions, budgets, goals, analytics, insights, reports, admin

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(accounts.router, prefix="/api/accounts", tags=["Accounts"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(budgets.router, prefix="/api/budgets", tags=["Budgets"])
app.include_router(goals.router, prefix="/api/goals", tags=["Goals"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)