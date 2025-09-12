FROM python:3.13-slim

WORKDIR /app

RUN pip install --no-cache-dir "poetry==2.1.0"

COPY pyproject.toml poetry.lock* /app/

ENV POETRY_VIRTUALENVS_IN_PROJECT=1 \
    PATH="/app/.venv/bin:$PATH"
RUN poetry install --no-root --only main

COPY ./app /app

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]