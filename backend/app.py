from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from collections import defaultdict
from routers.cars import router as cars_router
# from routers.users import router as users_router
from motor import motor_asyncio
from config import BaseConfig


settings = BaseConfig()

async def lifespan(app: FastAPI):
    app.client = motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
    app.db = app.client[settings.DB_NAME]
    try:
        app.client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        print("Mongo address:", settings.DB_URL)
    except Exception as e:
        print("Could not connect to MongoDB:", e)
    yield
    app.client.close()

app = FastAPI(lifespan=lifespan)
app.include_router(cars_router, prefix="/cars", tags=["cars"])
# app.include_router(users_router, prefix="/users", tags=["users"])

@app.get("/")
async def read_root():
    return {"Message": "Root Endpoint"}