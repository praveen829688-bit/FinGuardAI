from datetime import datetime

from fastapi import APIRouter

from app.database.connection import engine


router = APIRouter(
    prefix="/api/system",
    tags=["System"]
)


@router.get("/health")
def health():

    database = "OK"

    try:
        with engine.connect():
            pass
    except Exception:
        database = "ERROR"

    return {
        "status": (
            "OK"
            if database == "OK"
            else "DEGRADED"
        ),
        "service": "FinGuard AI",
        "database": database,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/security")
def security_status():

    return {
        "authentication": "JWT",
        "authorization": "USER_SCOPED",
        "security_events": "ENABLED",
        "fraud_detection": "ENABLED",
        "risk_intelligence": "ENABLED",
        "notification_system": "ENABLED",
        "api_documentation": "ENABLED"
    }


@router.get("/version")
def version():

    return {
        "application": "FinGuard AI",
        "version": "1.0.0",
        "stage": "PRODUCTION_READY"
    }
