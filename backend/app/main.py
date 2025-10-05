from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.core.config import settings
from app.core.database import get_db, engine
from app.models import Base
from app.api import auth, users, teams, challenges, submissions, admin, monitoring

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CyberCTF Arena",
    description="CTF Competition Platform",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение API endpoints
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(teams.router, prefix="/api/teams", tags=["teams"])
app.include_router(challenges.router, prefix="/api/challenges", tags=["challenges"])
app.include_router(submissions.router, prefix="/api/submissions", tags=["submissions"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["monitoring"])

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CyberCTF Arena"}

# Обслуживание статических файлов фронтенда
@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/{path:path}")
async def serve_frontend(path: str):
    frontend_path = f"frontend/{path}"
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return FileResponse('frontend/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)