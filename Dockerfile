# ─────────────────────────────────────────────────────────────────────────────
# Dockerfile for rag-chat-storage: installs root + service requirements,
# copies generated *_pb2.py files to /app so unqualified imports work,
# forces SQLAlchemy to use a local SQLite file for tests,
# and finally runs pytest.
# ─────────────────────────────────────────────────────────────────────────────

# 1) Start from Python 3.11 slim
FROM python:3.11-slim

# 2) Prevent writing .pyc and force unbuffered stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3) Create and switch to /app
WORKDIR /app

# 4) Copy only the root pyproject.toml first (for caching)
COPY pyproject.toml .

# 5) Install root-level dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -e .

# 6) Copy everything (project root) into /app
COPY . .

# 7) Install test dependencies
RUN pip install --no-cache-dir -e ".[test]"

# 8) Copy each service’s generated *_pb2.py and *_pb2_grpc.py files up into /app
#    so that "import session_pb2" etc. can be resolved at top level.
RUN cp src/db_service/db_service_pb2.py src/db_service/db_service_pb2_grpc.py  ./ \
 && cp src/session_service/session_pb2.py src/session_service/session_pb2_grpc.py  ./ \
 && cp src/message_service/message_pb2.py src/message_service/message_pb2_grpc.py  ./ \
 && cp src/api_gateway/session_pb2.py src/api_gateway/session_pb2_grpc.py  ./ \
 && cp src/api_gateway/message_pb2.py src/api_gateway/message_pb2_grpc.py  ./

# 9) Ensure /app and each service folder is on PYTHONPATH
#    This also allows bare "import dependencies" if dependencies.py lives in any one of these.
ENV PYTHONPATH="/app:/app/src/api_gateway:/app/src/db_service:/app/src/message_service:/app/src/session_service"

# 10) Force SQLAlchemy to use a local SQLite file, so that any code/tests
#     which rely on DATABASE_URL will not try to connect to "db".
ENV DATABASE_URL="sqlite:///./test.db"

# 11) Default command: run pytest (all tests under /app/tests/)
CMD ["pytest", "--maxfail=1", "--disable-warnings", "-q"]
