import json
from fastapi import FastAPI,Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pathlib
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict



class Settings(BaseSettings):
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings():
    return Settings()

DEBUG=get_settings().debug


BASE_DIR=pathlib.Path(__file__).parent
print(BASE_DIR/"templates")
app=FastAPI()
templates=Jinja2Templates(directory=str(BASE_DIR/"templates"))

@app.get("/",response_class=HTMLResponse) # HTTP GET
def home_view(request: Request, settings:Settings = Depends(get_settings)):
    print(settings.debug)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"abc": 123}
    )


@app.post("/") # HTTP POST
def home_detailed_view():
    return {"Hello: World"}


@app.post("/img-echo/") # HTTP POST
def img_echo_view(file):
    return {"Hello: World"}
