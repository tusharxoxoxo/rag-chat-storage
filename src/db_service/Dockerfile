FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .
COPY src/db_service/ .
EXPOSE 50050
CMD ["python", "main.py"]
