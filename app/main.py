import json
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pathlib


BASE_DIR=pathlib.Path(__file__).parent
print(BASE_DIR/"templates")
app=FastAPI()
templates=Jinja2Templates(directory=str(BASE_DIR/"templates"))

@app.get("/",response_class=HTMLResponse) # HTTP GET
def home_view(request: Request):
    return templates.TemplateResponse(
        request,
        "home.html",
        {"abc": 123}
    )


@app.post("/") # HTTP POST
def home_detailed_view():
    return {"Hello: World"}
