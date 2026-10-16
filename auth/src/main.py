from fastapi import FastAPI
from src.auth.api.router import router

app = FastAPI(root_path="/api")

app.include_router(router)


@app.get("/")
async def home():
    return {"message": "Hello world"}
