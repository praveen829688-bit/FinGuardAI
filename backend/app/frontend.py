from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse


def register_frontend(app: FastAPI):

    frontend_path = (
        Path(__file__).resolve().parent.parent
        / "frontend"
        / "index.html"
    )

    @app.get("/", include_in_schema=False)
    async def dashboard():

        if frontend_path.exists():
            return FileResponse(
                str(frontend_path),
                media_type="text/html"
            )

        return {
            "application": "FinGuard AI",
            "message": "Frontend file not found",
            "status": "error"
        }
