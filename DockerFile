FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "poetry run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
