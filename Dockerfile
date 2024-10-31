FROM python:3.12.5-alpine3.20

RUN apk add --update python3 py3-pip build-base

RUN pip3 install ruff

WORKDIR /app

COPY requirements.txt ./
RUN pip3 install -r ./requirements.txt

COPY app ./
COPY tests ./tests

# Run Linting
RUN ruff check /app

# Run Test
ENV ENVIRONMENT=test
ENV DATABASE_URL=sqlite:///:memory:
RUN python3 -m pytest tests/test_health.py

ENV PYTHONPATH=/ \
    PYTHONUNBUFFERED=1

EXPOSE 8080 5678

ENTRYPOINT ["uvicorn", "app.asgi:app", "--host", "0.0.0.0", "--port", "8080", \
            "--workers", "5", "--timeout-keep-alive", "300", "--timeout-graceful-shutdown", "120", \
            "--backlog", "2048"]