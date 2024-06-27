from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import memes, media, auth
from app.database import engine, Base

def create_app():
    # Создаем все таблицы в базе данных
    Base.metadata.create_all(bind=engine)

    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Публичный API
    app.include_router(memes.router, prefix="/api/v1/memes", tags=["memes"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

    # Приватный API
    app.include_router(media.router, prefix="/api/v1/media", tags=["media"])

    return app

app = create_app()
