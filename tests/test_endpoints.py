import io
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR
from PIL import Image, ImageDraw

client = TestClient(app)


def get_or_create_test_image():
    img_saved_path = BASE_DIR / "images"
    img_saved_path.mkdir(exist_ok=True)
    sample_img = img_saved_path / "test.png"
    if not sample_img.exists():
        # Create an image with readable text for OCR
        img = Image.new("RGB", (200, 100), color="white")
        draw = ImageDraw.Draw(img)
        draw.text((20, 40), "HELLO OCR", fill="black")
        img.save(sample_img, format="PNG")
    return sample_img


def test_get_home():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers['content-type']


def test_post_home_prediction():
    sample_img = get_or_create_test_image()
    with open(sample_img, "rb") as f:
        response = client.post("/", files={'file': (sample_img.name, f, 'image/png')})
    assert response.status_code == 200
    assert "application/json" in response.headers['content-type']
    data = response.json()
    assert "results" in data
    assert "filename" in data


def test_img_echo_valid():
    sample_img = get_or_create_test_image()
    with open(sample_img, 'rb') as f:
        response = client.post("/img-echo/", files={'file': (sample_img.name, f, 'image/png')})
    assert response.status_code == 200
    assert "image/" in response.headers['content-type']


def test_img_upload_invalid_extension():
    response = client.post(
        "/",
        files={'file': ('document.txt', b"Hello plain text", 'text/plain')}
    )
    assert response.status_code == 400
    assert "Unsupported file extension" in response.json()["detail"]


def test_img_upload_corrupted_image():
    response = client.post(
        "/",
        files={'file': ('corrupted.png', b"Not an actual image file", 'image/png')}
    )
    assert response.status_code == 400
    assert "Corrupted or invalid image" in response.json()["detail"]


def test_img_upload_empty_file():
    response = client.post(
        "/",
        files={'file': ('empty.png', b"", 'image/png')}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"]
