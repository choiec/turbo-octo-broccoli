FROM python:3.12-slim-bookworm
WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

COPY main.py ./
COPY app ./app
COPY data ./data
COPY entrypoint.sh /app/entrypoint.sh

RUN useradd --create-home appuser && chown -R appuser:appuser /app
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/app/entrypoint.sh"]
