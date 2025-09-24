# RAG Chat Storage API

A FastAPI-based service for managing chat sessions and messages.

## Quick Start

```bash
uv run fastapi dev main.py
```

## API Endpoints

### Session Management

#### Create Session

```http
POST /sessions
Content-Type: application/json

{
  "name": "My Chat Session",
  "description": "Optional description"
}
```

#### List Sessions

```http
GET /sessions
```

#### Get Session

```http
GET /sessions/{session_id}
```

#### Update Session

```http
PUT /sessions/{session_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description"
}
```

#### Delete Session

```http
DELETE /sessions/{session_id}
```

### Message Management

#### Add Message

```http
POST /sessions/{session_id}/messages
Content-Type: application/json

{
  "content": "Hello, how are you?",
  "role": "user",
  "metadata": {"optional": "data"}
}
```

#### Get Messages

```http
GET /sessions/{session_id}/messages?limit=10&offset=0
```

#### Get Specific Message

```http
GET /sessions/{session_id}/messages/{message_id}
```

#### Delete Message

```http
DELETE /sessions/{session_id}/messages/{message_id}
```

### Health Check

```http
GET /health
```

## Data Models

### Session

- `id`: Unique session identifier
- `name`: Session name
- `description`: Optional description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Message

- `id`: Unique message identifier
- `session_id`: Parent session ID
- `content`: Message content
- `role`: "user" or "assistant"
- `metadata`: Optional metadata dictionary
- `created_at`: Creation timestamp
