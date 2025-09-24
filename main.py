from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RAG Chat Storage", version="0.1.0")

# In-memory storage
sessions: Dict[str, Dict] = {}
messages: Dict[str, List[Dict]] = {}


# Data models
class SessionCreate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    name: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    metadata: Optional[Dict] = None


class MessageResponse(BaseModel):
    id: str
    session_id: str
    content: str
    role: str
    metadata: Optional[Dict]
    created_at: datetime


# Session Management APIs
@app.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate):
    """Create a new chat session."""
    session_id = str(uuid4())
    now = datetime.utcnow()

    session_data = {
        "id": session_id,
        "name": session.name or f"Session {session_id[:8]}",
        "description": session.description,
        "created_at": now,
        "updated_at": now,
    }

    sessions[session_id] = session_data
    messages[session_id] = []

    return SessionResponse(**session_data)


@app.get("/sessions", response_model=List[SessionResponse])
def list_sessions():
    """List all chat sessions."""
    return [SessionResponse(**session) for session in sessions.values()]


@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    """Get a specific chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(**sessions[session_id])


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    """Delete a chat session and all its messages."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    if session_id in messages:
        del messages[session_id]

    return {"message": "Session deleted successfully"}


@app.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(session_id: str, session: SessionCreate):
    """Update a chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    sessions[session_id].update(
        {
            "name": session.name or sessions[session_id]["name"],
            "description": session.description,
            "updated_at": datetime.utcnow(),
        }
    )

    return SessionResponse(**sessions[session_id])


# Message Management APIs
@app.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def add_message(session_id: str, message: MessageCreate):
    """Add a message to a chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    message_id = str(uuid4())
    now = datetime.utcnow()

    message_data = {
        "id": message_id,
        "session_id": session_id,
        "content": message.content,
        "role": message.role,
        "metadata": message.metadata,
        "created_at": now,
    }

    messages[session_id].append(message_data)
    sessions[session_id]["updated_at"] = now

    return MessageResponse(**message_data)


@app.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(session_id: str, limit: Optional[int] = None, offset: int = 0):
    """Retrieve messages from a chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_messages = messages.get(session_id, [])

    # Apply pagination
    start = offset
    end = offset + limit if limit else len(session_messages)

    return [MessageResponse(**msg) for msg in session_messages[start:end]]


@app.get("/sessions/{session_id}/messages/{message_id}", response_model=MessageResponse)
def get_message(session_id: str, message_id: str):
    """Get a specific message from a chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_messages = messages.get(session_id, [])
    message = next((msg for msg in session_messages if msg["id"] == message_id), None)

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    return MessageResponse(**message)


@app.delete("/sessions/{session_id}/messages/{message_id}")
def delete_message(session_id: str, message_id: str):
    """Delete a specific message from a chat session."""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session_messages = messages.get(session_id, [])
    message_index = next(
        (i for i, msg in enumerate(session_messages) if msg["id"] == message_id), None
    )

    if message_index is None:
        raise HTTPException(status_code=404, detail="Message not found")

    del session_messages[message_index]
    sessions[session_id]["updated_at"] = datetime.utcnow()

    return {"message": "Message deleted successfully"}


# Health check
@app.get("/")
def read_root():
    return {"message": "RAG Chat Storage API", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "sessions_count": len(sessions)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
