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
from starlette.responses import RedirectResponse, JSONResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request=request, name="mainpage.html"
    )

@app.get("/{short_url}")
async def short_url_handler(short_url: str):
    async with aiofiles.open("urls.json", mode='r') as f:
        urls_data = json.loads(await f.read())
    longurl = urls_data.get(short_url)
    return RedirectResponse(longurl)

@app.post("/")
async def create_url(longurl: Annotated[str, Form()]):
    alphabet = string.ascii_letters + string.digits
    short_url = ''.join(secrets.choice(alphabet) for _ in range(6))

    async with aiofiles.open("urls.json", mode='r') as f:
        urls_data = json.loads(await f.read())

    urls_data[short_url] = longurl

    async with aiofiles.open("urls.json", mode='w') as f:
        await f.write(json.dumps(urls_data, indent=4))
    return JSONResponse({"short_url": short_url, "longurl": longurl})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)