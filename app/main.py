import io
import pathlib
import uuid
from functools import lru_cache
from fastapi import FastAPI, Request, Depends, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic_settings import BaseSettings, SettingsConfigDict
from PIL import Image, UnidentifiedImageError
import pytesseract


class Settings(BaseSettings):
    debug: bool = False
    echo_active: bool = False

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()


DEBUG = get_settings().debug

BASE_DIR = pathlib.Path(__file__).parent
UPLOADED_DIR = BASE_DIR / "uploaded"
UPLOADED_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    print(settings.debug)
    return templates.TemplateResponse(
        request,
        "home.html",
        {"abc": 123}
    )


@app.post("/")
async def prediction_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    # 1. Read file bytes
    bytes_data = await file.read()
    if not bytes_data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # 2. Validate file extension
    fname = pathlib.Path(file.filename or "uploaded.png")
    fext = fname.suffix.lower()
    if fext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{fext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # 3. Validate image integrity & load image
    try:
        img = Image.open(io.BytesIO(bytes_data))
        img.verify()
        # Re-open for OCR because verify() closes/invalidates the stream
        img = Image.open(io.BytesIO(bytes_data))
    except (UnidentifiedImageError, Exception):
        raise HTTPException(status_code=400, detail="Corrupted or invalid image file.")

    # 4. Save uploaded image
    dest = UPLOADED_DIR / f"{uuid.uuid1()}{fext}"
    with open(dest, "wb") as out:
        out.write(bytes_data)

    # 5. Extract text using pytesseract
    ocr_text = pytesseract.image_to_string(img)

    return {
        "results": ocr_text.strip(),
        "filename": file.filename
    }


@app.post("/img-echo/", response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...), settings: Settings = Depends(get_settings)):
    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)

    bytes_data = await file.read()
    if not bytes_data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    fname = pathlib.Path(file.filename or "uploaded.png")
    fext = fname.suffix.lower()
    if fext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{fext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    try:
        with Image.open(io.BytesIO(bytes_data)) as img:
            img.verify()
    except (UnidentifiedImageError, Exception):
        raise HTTPException(status_code=400, detail="Corrupted or invalid image file.")

    dest = UPLOADED_DIR / f"{uuid.uuid1()}{fext}"
    with open(dest, "wb") as out:
        out.write(bytes_data)

    return FileResponse(dest)
