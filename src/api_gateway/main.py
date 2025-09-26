import uuid
from fastapi import FastAPI, Depends, Request
from dotenv import load_dotenv
from . import session_pb2, message_pb2
from .dependencies import verify_api_key
from . import stub_clients
import logging
from .custom_logging import request_id_var


load_dotenv()
app = FastAPI(title="API Gateway")

session_stub = stub_clients.get_session_stub()
message_stub = stub_clients.get_message_stub()


# FastAPI middleware to set the request ID
@app.middleware("http")
async def add_request_id_to_logs(request: Request, call_next):
    # Generate a unique request ID
    request_id = str(uuid.uuid4())
    # Set the request ID in the context variable
    request_id_var.set(request_id)

    # Process the request
    response = await call_next(request)

    return response


@app.get("/health")
def health():
    return {"status": "OK"}


@app.post("/sessions", dependencies=[Depends(verify_api_key)])
def create_session(name: str):
    resp = session_stub.CreateSession(session_pb2.CreateSessionRequest(name=name))
    return {"id": resp.id, "name": resp.name, "is_favorite": resp.is_favorite}


@app.get("/sessions", dependencies=[Depends(verify_api_key)])
def list_sessions():
    resp = session_stub.ListSessions(session_pb2.Empty())
    return [
        {"id": s.id, "name": s.name, "is_favorite": s.is_favorite}
        for s in resp.sessions
    ]


@app.patch("/sessions/{id}", dependencies=[Depends(verify_api_key)])
def update_session(id: int, name: str = None, is_favorite: bool = False):
    resp = session_stub.UpdateSession(
        session_pb2.UpdateSessionRequest(
            id=id, name=name or "", is_favorite=is_favorite
        )
    )
    return {"id": resp.id, "name": resp.name, "is_favorite": resp.is_favorite}


@app.delete("/sessions/{id}", status_code=204, dependencies=[Depends(verify_api_key)])
def delete_session(id: int):
    session_stub.DeleteSession(session_pb2.SessionId(id=id))
    return


@app.post("/sessions/{session_id}/messages", dependencies=[Depends(verify_api_key)])
def create_message(session_id: int, sender: str, content: str, context: str = ""):
    m = message_stub.CreateMessage(
        message_pb2.CreateMessageRequest(
            session_id=session_id, sender=sender, content=content, context=context
        )
    )
    return {
        "id": m.id,
        "session_id": m.session_id,
        "sender": m.sender,
        "content": m.content,
        "context": m.context,
    }


@app.get("/sessions/{session_id}/messages", dependencies=[Depends(verify_api_key)])
def list_messages(session_id: int, skip: int = 0, limit: int = 50):
    resp = message_stub.ListMessages(
        message_pb2.ListMessagesRequest(session_id=session_id, skip=skip, limit=limit)
    )
    return [
        {
            "id": m.id,
            "session_id": m.session_id,
            "sender": m.sender,
            "content": m.content,
            "context": m.context,
        }
        for m in resp.messages
    ]
