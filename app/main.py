from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

import app.models
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.deps import get_db
from app.routers.assets import router as assets_router
from app.routers.auth import router as auth_router
from app.routers.incidents import router as incidents_router
from app.routers.stats import router as stats_router

app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
)


@app.on_event("startup")
def on_startup():
    if not settings.TESTING:
        Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API working"}


@app.get("/health/db")
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"database": "connected"}


app.include_router(auth_router)
app.include_router(assets_router)
app.include_router(incidents_router)
app.include_router(stats_router)