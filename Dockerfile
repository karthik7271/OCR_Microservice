FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /code

# 1. Install system & Python dependencies (stays cached)
COPY ./requirements.txt /code/requirements.txt

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tesseract-ocr \
    build-essential \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get remove -y --purge build-essential \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy code & entrypoint
COPY ./app /code/app
COPY ./entrypoint.sh /code/entrypoint.sh

RUN chmod +x /code/entrypoint.sh

EXPOSE 8080

CMD ["/code/entrypoint.sh"]
