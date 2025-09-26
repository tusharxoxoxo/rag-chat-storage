# tests/test_session_service.py

import pytest
import grpc
from unittest.mock import MagicMock

from src.session_service.main import SessionServiceServicer

# Create a fake DB stub with MagicMock methods
class FakeDBStub:
    def __init__(self):
        self.CreateSession = MagicMock()
        self.ListSessions = MagicMock()
        self.UpdateSession = MagicMock()
        self.DeleteSession = MagicMock()

@pytest.fixture(autouse=True)
def patch_db_stub(monkeypatch):
    """
    Monkey-patch get_db_stub() in session_service.main so it returns FakeDBStub.
    """
    fake = FakeDBStub()
    monkeypatch.setattr("src.session_service.main.get_db_stub", lambda: fake)
    return fake

def test_create_session_happy(patch_db_stub):
    from src.session_service import session_pb2

    fake_stub = patch_db_stub
    fake_response = session_pb2.Session(id=42, name="Hello", is_favorite=False)
    fake_stub.CreateSession.return_value = fake_response

    servicer = SessionServiceServicer()
    req = session_pb2.CreateSessionRequest(name="Hello")
    resp = servicer.CreateSession(req, ctx=None)

    fake_stub.CreateSession.assert_called_once()
    called_req = fake_stub.CreateSession.call_args[0][0]
    assert called_req.name == "Hello"
    assert resp == fake_response

def test_list_sessions_happy(patch_db_stub):
    from src.session_service import session_pb2

    fake_stub = patch_db_stub
    fake_response = session_pb2.SessionList(sessions=[
        session_pb2.Session(id=1, name="A", is_favorite=False),
        session_pb2.Session(id=2, name="B", is_favorite=True),
    ])
    fake_stub.ListSessions.return_value = fake_response

    servicer = SessionServiceServicer()
    resp = servicer.ListSessions(session_pb2.Empty(), ctx=None)

    fake_stub.ListSessions.assert_called_once()
    assert resp == fake_response

def test_update_session_happy(patch_db_stub):
    from src.session_service import session_pb2

    fake_stub = patch_db_stub
    fake_response = session_pb2.Session(id=5, name="Z", is_favorite=True)
    fake_stub.UpdateSession.return_value = fake_response

    servicer = SessionServiceServicer()
    req = session_pb2.UpdateSessionRequest(id=5, name="Z", is_favorite=True)
    resp = servicer.UpdateSession(req, ctx=None)

    fake_stub.UpdateSession.assert_called_once()
    called_req = fake_stub.UpdateSession.call_args[0][0]
    assert called_req.id == 5
    assert called_req.name == "Z"
    assert called_req.is_favorite is True
    assert resp == fake_response

def test_delete_session_happy(patch_db_stub):
    from src.session_service import session_pb2

    fake_stub = patch_db_stub
    fake_stub.DeleteSession.return_value = session_pb2.Empty()

    servicer = SessionServiceServicer()
    req = session_pb2.SessionId(id=123)
    resp = servicer.DeleteSession(req, ctx=None)

    fake_stub.DeleteSession.assert_called_once()
    called_req = fake_stub.DeleteSession.call_args[0][0]
    assert called_req.id == 123
    assert resp is not None

def test_create_session_unhappy_db_raises(monkeypatch):
    from src.session_service import session_pb2

    fake_stub = MagicMock()
    fake_stub.CreateSession.side_effect = grpc.RpcError("DB-side failure")
    monkeypatch.setattr("session_service.main.get_db_stub", lambda: fake_stub)

    servicer = SessionServiceServicer()
    req = session_pb2.CreateSessionRequest(name="FailMe")
    with pytest.raises(grpc.RpcError):
        _ = servicer.CreateSession(req, ctx=None)

def test_list_sessions_unhappy_db_raises(monkeypatch):
    from src.session_service import session_pb2

    fake_stub = MagicMock()
    fake_stub.ListSessions.side_effect = grpc.RpcError("DB broke")
    monkeypatch.setattr("session_service.main.get_db_stub", lambda: fake_stub)

    servicer = SessionServiceServicer()
    with pytest.raises(grpc.RpcError):
        _ = servicer.ListSessions(session_pb2.Empty(), ctx=None)

def test_update_session_unhappy_db_raises(monkeypatch):
    from src.session_service import session_pb2

    fake_stub = MagicMock()
    fake_stub.UpdateSession.side_effect = grpc.RpcError("cannot update")
    monkeypatch.setattr("session_service.main.get_db_stub", lambda: fake_stub)

    servicer = SessionServiceServicer()
    req = session_pb2.UpdateSessionRequest(id=50, name="X", is_favorite=False)
    with pytest.raises(grpc.RpcError):
        _ = servicer.UpdateSession(req, ctx=None)

def test_delete_session_unhappy_db_raises(monkeypatch):
    from src.session_service import session_pb2

    fake_stub = MagicMock()
    fake_stub.DeleteSession.side_effect = grpc.RpcError("cannot delete")
    monkeypatch.setattr("session_service.main.get_db_stub", lambda: fake_stub)

    servicer = SessionServiceServicer()
    req = session_pb2.SessionId(id=999)
    with pytest.raises(grpc.RpcError):
        _ = servicer.DeleteSession(req, ctx=None)
