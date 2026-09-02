import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return "Hello from Freelance lite"

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8080, host="127.0.0.1")