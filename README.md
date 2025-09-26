# RAG Chat Storage

A microservices-based RAG chat storage system using FastAPI, gRPC, and PostgreSQL.

## Quick Start

```bash
# Install dependencies
uv venv .venv
source .venv/bin/activate
uv sync

# Start all services
chmod +x run.sh
./run.sh
```

API Gateway: http://localhost:8000  
Swagger UI: http://localhost:8000/docs

- Generate any missing gRPC stubs (via `make proto`)
- Build and start all containers/services using Docker Compose
- Expose the API Gateway on port 8000

5. **Verify that services are running**
   - PostgreSQL will be on port 5432
   - gRPC DB Service on port 50050
   - gRPC Session Service on port 50051
   - gRPC Message Service on port 50052
   - FastAPI API Gateway on port 8000

---

## Swagger / OpenAPI Documentation

Once the application is running, open your browser and navigate to:

```
http://localhost:8000/docs
```

The Swagger UI allows you to explore and test all REST endpoints exposed by the API Gateway. You can view request parameters, response schemas, and try out example requests directly from the browser.

---

## Available APIs (Overview)

> **Note**: All non-health endpoints require an API key header `X-API-Key: <your_api_key>` in the request. Configure this value in your `.env` file before running.

### Health Check

- **GET /health**
  - **Description**: Returns a simple “OK” status to verify the API Gateway is up.
  - **Authentication**: None

### Session Endpoints

- **POST /sessions**
  - Create a new chat session (body parameter: `name`)
- **GET /sessions**
  - List all chat sessions
- **PATCH /sessions/{id}**
  - Update a session’s `name` and/or `is_favorite` flag
- **DELETE /sessions/{id}**
  - Delete a session by its ID

### Message Endpoints

- **POST /sessions/{session_id}/messages**
  - Add a new message to a specific session (parameters: `sender`, `content`, `context`)
- **GET /sessions/{session_id}/messages**
  - Retrieve messages for a given session (supports `skip` and `limit` for pagination)

All endpoints and their request/response formats are documented and can be tested via Swagger UI.

---

## Notes

- Copy `.env.example` to `.env` and fill in your configuration (PostgreSQL credentials, API key, etc.) before running.
- If you modify any `.proto` files, re-run `make proto` to regenerate gRPC stubs.
- To stop and remove all Docker containers and volumes (including the Postgres volume), run:
  ```bash
  docker-compose down -v
  ```

## Run Unit Tests

- Ensure you are in the main directory

```bash
   uv pip install -e ".[test]"
   docker build -t rag-chat-storage-tests .
   docker run --rm -it rag-chat-storage-tests pytest -vv --capture=no

# Stop services
docker-compose down -v
```

---
