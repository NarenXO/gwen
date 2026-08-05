from fastapi import FastAPI
from sqlalchemy import text
from core.database import engine
from core.database import Base, engine
from features.auth import models 
from features.auth.routes import router as auth_router
from features.analytics.routes import router as analytics_router



 # important: ensures models are registered
Base.metadata.create_all(bind=engine)
app = FastAPI(title="GWEN Backend")
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])



@app.get("/")
def health_check():
    return {"status": "GWEN backend running"}


@app.get("/db-test")
def db_test():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return {
                "database": "connected",
                "result": result.scalar()
            }
    except Exception as e:
        return {
            "database": "failed",
            "error": str(e)
        }