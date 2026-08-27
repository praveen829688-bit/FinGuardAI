from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from app import models
from app.models.bill import Bill
from app.models.credit_card import CreditCard
from app.models.debt import Debt
from app.api.accounts import router as accounts_router
from app.api.planning import router as planning_router
from app.api.credit import router as credit_router
from app.api.risk import router as risk_router
from app.api.reports import router as reports_router
from app.api.system import router as system_router
from app.api.investments import router as investments_router
from app.api.advisor import router as advisor_router
from app.api.analytics import router as analytics_router
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.dashboard import router as dashboard_router
from app.api.dashboard_monthly import router as dashboard_monthly_router
from app.api.notifications import router as notifications_router
from app.api.notification_history import router as notification_history_router
from app.api.phishing import router as phishing_router
from app.api.bills import router as bills_router
from app.api.security import router as security_router
from app.api.transactions import router as transactions_router
from app.database.connection import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    print("FinGuard AI database initialized successfully.")
    print("Financial models loaded successfully.")
    print("Financial APIs loaded successfully.")
    print("Security Center loaded successfully.")
    print("Notification Center loaded successfully.")
    print("Phishing Protection loaded successfully.")
    print("Financial Dashboard loaded successfully.")

    yield


app = FastAPI(
    title="FinGuard AI",
    description=(
        "AI-powered Financial Intelligence "
        "and Security Platform"
    ),
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(advisor_router)
app.include_router(analytics_router)
app.include_router(categories_router)
app.include_router(transactions_router)
app.include_router(security_router)
app.include_router(notifications_router)
app.include_router(notification_history_router)
app.include_router(phishing_router)
app.include_router(bills_router)
app.include_router(planning_router)
app.include_router(credit_router)
app.include_router(risk_router)
app.include_router(reports_router)
app.include_router(system_router)
app.include_router(investments_router)
app.include_router(dashboard_router)
app.include_router(dashboard_monthly_router)



@app.get("/api/health")
def health_check():
    return {
        "application": "FinGuard AI",
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/system")
def system_status():
    return {
        "platform": "FinGuard AI",
        "backend": "FastAPI",
        "database": "SQLite",
        "authentication": "JWT",
        "password_security": "Argon2",
        "financial_core": "enabled",
        "ai_fraud_engine": "enabled",
        "security_center": "enabled",
        "notification_center": "enabled",
        "phishing_protection": "enabled",
        "financial_dashboard": "enabled",
        "environment": "development",
        "status": "ready"
    }
from app.frontend import register_frontend

register_frontend(app)
