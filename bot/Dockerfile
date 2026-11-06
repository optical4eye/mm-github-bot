FROM python:3.15-slim

WORKDIR /app

RUN groupadd -r botuser && useradd -r -g botuser -d /app -s /sbin/nologin botuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chown -R botuser:botuser /app

USER botuser

CMD ["python", "main.py"]
