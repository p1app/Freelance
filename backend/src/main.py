from typing import Annotated

import fastapi_structured_logging
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from fastapi_jwt_harmony import JWTHarmonyException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.exceptions import AppException
from core.health_func import health_db, health_redis
from routers.admin_router import router as admin_router
from routers.auth_router import router as auth_router
from routers.chat_router import router as chat_router
from routers.contract_router import router as contract_router
from routers.milestone_router import router as milestone_router
from routers.notification_router import router as notification_router
from routers.project_router import router as project_router
from routers.proposal_router import router as proposal_router
from routers.review_router import router as review_router
from routers.user_router import router as user_router
from routers.ws_router import router as ws_router

# Опеределение logger'a
config = fastapi_structured_logging.AccessLogConfig(log_level="info")
fastapi_structured_logging.setup_logging()
logger = fastapi_structured_logging.get_logger()

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})
app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # ← Vite dev
        "http://127.0.0.1:5173",
        "http://frontend:5173",
        "http://prometheus:9090",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # ← разрешает все методы
    allow_headers=["*"],  # ← разрешает все заголовки
)
app.add_middleware(
    middleware_class=fastapi_structured_logging.AccessLogMiddleware, config=config
)

# Определение prometheus instrumentator
Instrumentator().instrument(app).expose(app)


app.include_router(auth_router)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(proposal_router)
app.include_router(review_router)
app.include_router(project_router)
app.include_router(milestone_router)
app.include_router(contract_router)
app.include_router(chat_router)
app.include_router(ws_router)
app.include_router(notification_router)
security = HTTPBearer()


@app.get("/", tags=["main"])
def root():
    return "Hello from Freelance lite"


@app.get("/health", tags=["main"])
async def health_endpoint(db: Annotated[AsyncSession, Depends(get_db)]):
    if await health_db(session=db) and await health_redis():
        return "The application is ready"
    else:
        raise HTTPException(status_code=503, detail="database is not ready")


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"detail": "Conflict"})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request, exc):
    detail = "; ".join(
        f"{'.'.join(str(p) for p in err['loc'][1:])}: {err['msg']}"
        for err in exc.errors()
    )
    return JSONResponse(status_code=422, content={"detail": detail})


@app.exception_handler(JWTHarmonyException)
async def jwt_exc_handler(request, exc):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        port=8000,
        host="0.0.0.0",
        log_config=None,
        access_log=False,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
