from fastapi import FastAPI
from sqlalchemy import text
from core.database import engine
from core.database import Base, engine
from features.auth import models 
from features.auth.routes import router as auth_router
from features.analytics.routes import router as analytics_router
from features.videos.routes import router as videos_router
from features.comments.routes import router as comments_router
from features.ai.routes import router as ai_router
from features.video_processing.routes import router as video_router, thumbnail_router
from fastapi.responses import JSONResponse
from fastapi import Request




 # important: ensures models are registered
Base.metadata.create_all(bind=engine)
app = FastAPI(title="GWEN Backend")
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
app.include_router(videos_router, prefix="/videos", tags=["Videos"])
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(ai_router, prefix="/ai", tags=["AI"])
app.include_router(video_router)
app.include_router(thumbnail_router)




@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=400,
        content={
            "error": "Something went wrong.",
            "details": str(exc)
        }
    )

@app.get("/")
def health_check():
    return {"status": "GWEN backend running"}


# ✅ Optional health check
@app.get("/health")
def health():
    return {"status": "ok"}

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