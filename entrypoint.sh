RUN_PORT=${PORT:- 8080}


/usr/local/bin uvicorn app.main:app --host 0.0.0.0 --port "${RUN_PORT}"
