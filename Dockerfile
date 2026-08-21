FROM python:3.12-slim

    # 1. Install dependencies first (stays cached)
    COPY ./requirements.txt /requirements.txt

    RUN apt-get update && \
        apt-get install -y \
        build-essential \
        python3-dev \
        tesseract-ocr \
        make \
        gcc \
        && python3 -m pip install -r requirements.txt \
        && apt-get remove -y --purge make gcc build-essential \
        && apt-get autoremove -y \
        && rm -rf /var/lib/apt/lists/*

    # 2. Copy code & scripts second (builds instantly when modified)
    COPY ./entrypoint.sh ./entrypoint.sh
    COPY ./app /app

    RUN chmod +x entrypoint.sh

    CMD ["./entrypoint.sh"]
