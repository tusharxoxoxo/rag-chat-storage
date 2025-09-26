import pytest
import grpc
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from src.api_gateway.main import app

from src.api_gateway import session_pb2, message_pb2

@pytest.fixture(autouse=True)
def patch_stubs(monkeypatch):
    fake_session_stub = MagicMock()
    fake_message_stub = MagicMock()

    # Replace get_session_stub and get_message_stub
    import src.api_gateway.stub_clients as sc
    monkeypatch.setattr(sc, 'get_session_stub', lambda: fake_session_stub)
    monkeypatch.setattr(sc, 'get_message_stub', lambda: fake_message_stub)

    return fake_session_stub, fake_message_stub

@pytest.fixture
def client():
    return TestClient(app)

def test_health_endpoint(client):
    """
    /health should always return 200 and {"status":"OK"}.
    """
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "OK"}


def test_create_session_endpoint_happy(client, patch_stubs):
    fake_session_stub, _ = patch_stubs

    # Prepare a fake gRPC response
    fake_session = session_pb2.Session(id=10, name="NewSess", is_favorite=False)
    fake_session_stub.CreateSession.return_value = fake_session

    payload = {"name": "NewSess"}
    resp = client.post("/sessions/", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 10
    assert data["name"] == "NewSess"
    assert data["is_favorite"] is False

    # Check that the stub was invoked with the correct proto request
    called_req = fake_session_stub.CreateSession.call_args[0][0]
    assert called_req.name == "NewSess"

def test_create_session_endpoint_unhappy_downstream(monkeypatch, client, patch_stubs):
    fake_session_stub, _ = patch_stubs

    # Simulate the stub raising a gRPC error
    fake_session_stub.CreateSession.side_effect = grpc.RpcError("DB fail")

    payload = {"name": "WillFail"}
    resp = client.post("/sessions/", json=payload)
    # When the gRPC stub raises, FastAPI should catch and return a 500
    assert resp.status_code == 500
    assert "DB fail" in resp.json().get("detail", "")

def test_list_sessions_endpoint_happy(client, patch_stubs):
    fake_session_stub, _ = patch_stubs

    fake_session_list = session_pb2.SessionList(sessions=[
        session_pb2.Session(id=1, name="A", is_favorite=False),
        session_pb2.Session(id=2, name="B", is_favorite=True),
    ])
    fake_session_stub.ListSessions.return_value = fake_session_list

    resp = client.get("/sessions/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    # Expect two sessions
    assert len(data) == 2
    assert data[0]["id"] == 1 and data[0]["name"] == "A"
    assert data[1]["id"] == 2 and data[1]["is_favorite"] is True

def test_list_sessions_endpoint_unhappy_downstream(client, patch_stubs):
    fake_session_stub, _ = patch_stubs
    fake_session_stub.ListSessions.side_effect = grpc.RpcError("ListFail")

    resp = client.get("/sessions/")
    assert resp.status_code == 500
    assert "ListFail" in resp.json().get("detail", "")

def test_update_session_endpoint_happy(client, patch_stubs):
    fake_session_stub, _ = patch_stubs

    fake_response = session_pb2.Session(id=5, name="X", is_favorite=True)
    fake_session_stub.UpdateSession.return_value = fake_response

    payload = {"name": "X", "is_favorite": True}
    resp = client.put("/sessions/5", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 5
    assert data["name"] == "X"
    assert data["is_favorite"] is True

    called_req = fake_session_stub.UpdateSession.call_args[0][0]
    assert called_req.id == 5
    assert called_req.name == "X"
    assert called_req.is_favorite is True

def test_update_session_endpoint_unhappy_downstream(client, patch_stubs):
    fake_session_stub, _ = patch_stubs
    fake_session_stub.UpdateSession.side_effect = grpc.RpcError("UpFail")

    payload = {"name": "X", "is_favorite": True}
    resp = client.put("/sessions/999", json=payload)
    assert resp.status_code == 500
    assert "UpFail" in resp.json().get("detail", "")

def test_delete_session_endpoint_happy(client, patch_stubs):
    fake_session_stub, _ = patch_stubs

    fake_session_stub.DeleteSession.return_value = session_pb2.Empty()
    resp = client.delete("/sessions/7")

    assert resp.status_code == 200
    assert resp.json() == {"detail": "Deleted"}  # According to our implementation

    called_req = fake_session_stub.DeleteSession.call_args[0][0]
    assert called_req.id == 7

def test_delete_session_endpoint_unhappy_downstream(client, patch_stubs):
    fake_session_stub, _ = patch_stubs
    fake_session_stub.DeleteSession.side_effect = grpc.RpcError("DelFail")

    resp = client.delete("/sessions/123")
    assert resp.status_code == 500
    assert "DelFail" in resp.json().get("detail", "")


def test_create_message_endpoint_happy(client, patch_stubs):
    _, fake_message_stub = patch_stubs

    fake_msg = message_pb2.Message(
        id=55, session_id=3, sender="Alice", content="Hello", context="ctx"
    )
    fake_message_stub.CreateMessage.return_value = fake_msg

    payload = {
        "session_id": 3,
        "sender": "Alice",
        "content": "Hello",
        "context": "ctx"
    }
    resp = client.post("/messages/", json=payload)

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == 55
    assert data["session_id"] == 3
    assert data["sender"] == "Alice"
    assert data["content"] == "Hello"
    assert data["context"] == "ctx"

    called_req = fake_message_stub.CreateMessage.call_args[0][0]
    assert called_req.session_id == 3
    assert called_req.sender == "Alice"
    assert called_req.content == "Hello"
    assert called_req.context == "ctx"

def test_create_message_endpoint_unhappy_downstream(client, patch_stubs):
    _, fake_message_stub = patch_stubs
    fake_message_stub.CreateMessage.side_effect = grpc.RpcError("MsgFail")

    payload = {
        "session_id": 999,
        "sender": "B",
        "content": "Hi",
        "context": "ctx"
    }
    resp = client.post("/messages/", json=payload)
    assert resp.status_code == 500
    assert "MsgFail" in resp.json().get("detail", "")

def test_list_messages_endpoint_happy(client, patch_stubs):
    _, fake_message_stub = patch_stubs

    fake_msg_list = message_pb2.MessageList(messages=[
        message_pb2.Message(id=2, session_id=3, sender="B", content="Hi", context="ctx")
    ])
    fake_message_stub.ListMessages.return_value = fake_msg_list

    resp = client.get("/messages/?session_id=3&skip=0&limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == 2
    assert data[0]["session_id"] == 3
    assert data[0]["content"] == "Hi"

def test_list_messages_endpoint_unhappy_downstream(client, patch_stubs):
    _, fake_message_stub = patch_stubs
    fake_message_stub.ListMessages.side_effect = grpc.RpcError("LstFail")

    resp = client.get("/messages/?session_id=3&skip=0&limit=10")
    assert resp.status_code == 500
    assert "LstFail" in resp.json().get("detail", "")
