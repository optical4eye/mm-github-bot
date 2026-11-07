# Build stage
FROM python:3.15-slim AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_CACHE=1

COPY requirements.txt .

RUN uv venv .venv && uv pip install -r requirements.txt


# Final stage
FROM python:3.15-slim

WORKDIR /app

RUN groupadd -r -g 10001 botuser && \
    useradd -r -g botuser -u 10001 -d /app -s /sbin/nologin botuser && \
    mkdir /data && chown botuser:botuser /data

COPY --from=builder /app/.venv /app/.venv

COPY . .

RUN chown -R botuser:botuser /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER botuser

CMD ["python", "main.py"]