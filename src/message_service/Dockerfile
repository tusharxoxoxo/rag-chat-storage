FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .
COPY src/message_service/ .
EXPOSE 50052
CMD ["python", "main.py"]
