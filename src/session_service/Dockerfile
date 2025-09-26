FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .
COPY src/session_service/ .
EXPOSE 50051
CMD ["python", "main.py"]
