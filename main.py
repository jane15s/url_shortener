import os
from typing import Union, Annotated
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Form
import json
import secrets
import string
import asyncio
import aiofiles
from pymongo import ReturnDocument
from starlette.responses import RedirectResponse, JSONResponse
import motor.motor_asyncio

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
mongo_host = os.environ.get("MONGO_HOST", "localhost")
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb://admin:password@{mongo_host}:27017")
db = mongo_client.shortener
urls_collection = db.urls

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="mainpage.html"
    )

@app.get("/{short_url}")
async def short_url_handler(short_url: str):
    urls_data = await urls_collection.find_one_and_update({"short_url": short_url}, {"$inc": {"clicks": 1}})
    longurl = urls_data.get("long_url")
    return RedirectResponse(longurl)

@app.post("/")
async def create_url(longurl: Annotated[str, Form()]):
    alphabet = string.ascii_letters + string.digits
    short_url = ''.join(secrets.choice(alphabet) for _ in range(6))
    await urls_collection.insert_one({"short_url": short_url, "long_url": longurl, "clicks": 0})
    return JSONResponse({"short_url": short_url, "longurl": longurl})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)