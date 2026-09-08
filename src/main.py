import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core.exceptions import AppException

app = FastAPI()


@app.get("/")
def root():
    return "Hello from Freelance lite"


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8080, host="127.0.0.1")
