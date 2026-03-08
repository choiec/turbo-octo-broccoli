FROM python:3.12-slim-bookworm
WORKDIR /app

# uv 설치
RUN pip install --no-cache-dir uv

# 의존성 먼저 복사 (캐시 활용)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project

# 소스 복사
COPY main.py ./
COPY app ./app
COPY entrypoint.sh /app/entrypoint.sh

# 비권한 사용자 (엔트리포인트가 /data chown 후 이 사용자로 앱 실행)
RUN useradd --create-home appuser && chown -R appuser:appuser /app
RUN chmod +x /app/entrypoint.sh

ENV API_PORT=54321
EXPOSE 54321
ENV PYTHONUNBUFFERED=1
ENTRYPOINT ["/app/entrypoint.sh"]
