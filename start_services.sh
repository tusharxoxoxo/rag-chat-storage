#!/bin/bash
# Start all RAG Chat Storage services
# This script starts all four services in the background

set -e

echo "Starting RAG Chat Storage services..."

# Set environment variables
export DATABASE_URL="sqlite:///./test.db"
export DB_SERVICE_ADDR="localhost:50050"
export API_KEY="test-api-key"
export SESSION_SERVICE_ADDR="localhost:50051"
export MESSAGE_SERVICE_ADDR="localhost:50052"

# Activate virtual environment
source .venv/bin/activate

# Start Database Service
echo "Starting Database Service on port 50050..."
python -m src.db_service.main &
DB_PID=$!

# Wait a moment for DB service to start
sleep 2

# Start Session Service
echo "Starting Session Service on port 50051..."
python -m src.session_service.main &
SESSION_PID=$!

# Start Message Service
echo "Starting Message Service on port 50052..."
python -m src.message_service.main &
MESSAGE_PID=$!

# Wait a moment for services to start
sleep 2

# Start API Gateway
echo "Starting API Gateway on port 8000..."
uvicorn src.api_gateway.main:app --host 0.0.0.0 --port 8000 &
GATEWAY_PID=$!

echo ""
echo "All services started!"
echo "Database Service PID: $DB_PID"
echo "Session Service PID: $SESSION_PID"
echo "Message Service PID: $MESSAGE_PID"
echo "API Gateway PID: $GATEWAY_PID"
echo ""
echo "API Gateway: http://localhost:8000"
echo "Swagger UI: http://localhost:8000/docs"
echo ""
echo "To stop all services, run: pkill -f 'python -m src' && pkill -f uvicorn"
echo "Or press Ctrl+C to stop this script (services will continue running)"

# Wait for user to stop
wait
