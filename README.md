# RAG Chat Storage

A microservices-based RAG chat storage system using FastAPI, gRPC, and PostgreSQL.

## Prerequisites

- **Python 3.11+** with `uv` package manager
- **Docker Desktop** (for Docker option)
- **Git** (for cloning the repository)

## Quick Start

> **⚠️ Important**: If you've run this project before, stop existing services first:
>
> ```bash
> pkill -f "python -m src" && pkill -f "uvicorn" && docker-compose down
> ```
>
> **🚀 For the best experience, use Option 2 (Run Locally) below, as the Docker setup currently has import issues.**

### Option 1: Run with Docker (Recommended for Production)

> **⚠️ Note**: The Docker setup currently has import issues. For a working setup, use **Option 2 (Run Locally)** below.

```bash
# 1. Install dependencies
uv venv .venv
source .venv/bin/activate
uv sync

# 2. Install grpcio-tools for protocol buffer generation
uv add grpcio-tools

# 3. Generate gRPC protocol buffer stubs
source .venv/bin/activate
make proto

# 4. Create .env file with required environment variables
cat > .env << EOF
# Database Configuration
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=rag_chat_storage
DATABASE_URL=postgresql://postgres:password@db:5432/rag_chat_storage

# API Configuration
API_KEY=your-secret-api-key-here
RATE_LIMIT=100
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
EOF

# 5. Fix import statements in generated files (REQUIRED)
# The generated gRPC files need relative imports fixed. Run these commands:

# Fix db_service imports
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/db_service/db_service_pb2_grpc.py
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/session_service/db_service_pb2_grpc.py
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/message_service/db_service_pb2_grpc.py

# Fix session_service imports
sed -i '' 's/import session_pb2 as session__pb2/from . import session_pb2 as session__pb2/g' src/session_service/session_pb2_grpc.py
sed -i '' 's/import session_pb2 as session__pb2/from . import session_pb2 as session__pb2/g' src/api_gateway/session_pb2_grpc.py

# Fix message_service imports
sed -i '' 's/import message_pb2 as message__pb2/from . import message_pb2 as message__pb2/g' src/message_service/message_pb2_grpc.py
sed -i '' 's/import message_pb2 as message__pb2/from . import message_pb2 as message__pb2/g' src/api_gateway/message_pb2_grpc.py

# 6. Start all services with Docker
chmod +x run.sh
./run.sh
```

### Option 2: Run Locally (Development) - **RECOMMENDED**

> **✅ This is the working option. Use this for development and testing.**

```bash
# 1. Install dependencies
uv venv .venv
source .venv/bin/activate
uv sync

# 2. Install grpcio-tools for protocol buffer generation
uv add grpcio-tools

# 3. Generate gRPC protocol buffer stubs
source .venv/bin/activate
make proto

# 4. Fix import statements in generated files (REQUIRED)
# The generated gRPC files need relative imports fixed. Run these commands:

# Fix db_service imports
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/db_service/db_service_pb2_grpc.py
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/session_service/db_service_pb2_grpc.py
sed -i '' 's/import db_service_pb2 as db__service__pb2/from . import db_service_pb2 as db__service__pb2/g' src/message_service/db_service_pb2_grpc.py

# Fix session_service imports
sed -i '' 's/import session_pb2 as session__pb2/from . import session_pb2 as session__pb2/g' src/session_service/session_pb2_grpc.py
sed -i '' 's/import session_pb2 as session__pb2/from . import session_pb2 as session__pb2/g' src/api_gateway/session_pb2_grpc.py

# Fix message_service imports
sed -i '' 's/import message_pb2 as message__pb2/from . import message_pb2 as message__pb2/g' src/message_service/message_pb2_grpc.py
sed -i '' 's/import message_pb2 as message__pb2/from . import message_pb2 as message__pb2/g' src/api_gateway/message_pb2_grpc.py

# 4. Set environment variables
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"

# 5. Start all services (run each in a separate terminal)
# Terminal 1 - Database Service
source .venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"
python -m src.db_service.main

# Terminal 2 - Session Service
source .venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"
python -m src.session_service.main

# Terminal 3 - Message Service
source .venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"
python -m src.message_service.main

# Terminal 4 - API Gateway
source .venv/bin/activate
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"
uvicorn src.api_gateway.main:app --host 0.0.0.0 --port 8000
```

**API Gateway**: http://localhost:8000  
**Swagger UI**: http://localhost:8000/docs

### Service Ports

- **Database Service** (gRPC): Port 50050
- **Session Service** (gRPC): Port 50051
- **Message Service** (gRPC): Port 50052
- **API Gateway** (FastAPI): Port 8000
- **Database**: SQLite (test.db) for local development

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

## Testing the API

Once all services are running, you can test the API:

```bash
# Test health endpoint (no API key required)
curl http://localhost:8000/health

# Test session creation
curl -X POST -H "X-API-Key: test-api-key" "http://localhost:8000/sessions?name=Test%20Session"

# List sessions
curl -H "X-API-Key: test-api-key" http://localhost:8000/sessions

# Create a message in session 1
curl -X POST -H "X-API-Key: test-api-key" "http://localhost:8000/sessions/1/messages?sender=user&content=Hello%20World&context=test"

# List messages for session 1
curl -H "X-API-Key: test-api-key" http://localhost:8000/sessions/1/messages
```

### Expected Responses

- **Health Check**: `{"status":"OK"}`
- **Session Creation**: `{"id":1,"name":"Test Session","is_favorite":false}`
- **Session List**: `[{"id":1,"name":"Test Session","is_favorite":false}]`
- **Message Creation**: `{"id":1,"session_id":1,"sender":"user","content":"Hello World","context":"test"}`

---

## Troubleshooting

### Common Issues

1. **Docker import errors**: The Docker setup currently has issues with relative imports. Use the local development option (Option 2) instead.

2. **Missing grpcio-tools**: If you see "ModuleNotFoundError: No module named 'grpc_tools'", run:

   ```bash
   source .venv/bin/activate
   uv add grpcio-tools
   ```

3. **Import errors in gRPC files**: The generated gRPC files need relative imports fixed. This is REQUIRED after running `make proto`. Use the provided `sed` commands in the setup instructions.

4. **Services not starting**: Make sure all environment variables are set and each service is running in its own terminal.

5. **Database connection issues**: For local development, the system uses SQLite (test.db). For Docker, it uses PostgreSQL.

6. **Port conflicts**: Ensure ports 50050, 50051, 50052, 8000, and 5432 are not in use by other applications.

7. **Missing .env file**: Docker Compose requires a `.env` file with all environment variables. Use the provided template above.

8. **ModuleNotFoundError**: If you see "No module named 'db_service_pb2'" errors, you need to run the import fix commands after `make proto`.

9. **Port already in use**: If you see "address already in use" errors, stop existing services first:

   ```bash
   # Stop all running services
   pkill -f "python -m src"
   pkill -f "uvicorn"
   docker-compose down

   # Check what's using the ports
   lsof -i :8000
   lsof -i :50050
   lsof -i :50051
   lsof -i :50052
   ```

### Verifying Services

```bash
# Check if services are running
ps aux | grep python

# Test individual service endpoints
curl http://localhost:8000/health

# Check which ports are in use
lsof -i :8000
lsof -i :50050
lsof -i :50051
lsof -i :50052
```

### Stopping Services

```bash
# Stop all Python processes (if running locally)
pkill -f "python -m src"
pkill -f "uvicorn"

# Stop Docker services
docker-compose down

# Stop and remove Docker volumes (clean slate)
docker-compose down -v
```

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

# Stop all the services
docker-compose down -v
```

---
