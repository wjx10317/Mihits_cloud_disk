from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, file, folder, trash
from app.middleware.error_handler import AppException, app_exception_handler

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_exception_handler(AppException, app_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(file.router)
app.include_router(folder.router)
app.include_router(trash.router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
