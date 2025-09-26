# tests/test_message_service.py

import pytest
import grpc
from unittest.mock import MagicMock

from src.message_service.main import MessageServiceServicer

# Fake DB stub for message_service
class FakeDBStub:
    def __init__(self):
        self.CreateMessage = MagicMock()
        self.ListMessages = MagicMock()

@pytest.fixture(autouse=True)
def patch_db_stub(monkeypatch):
    """
    Replace get_db_stub() in message_service.main to return FakeDBStub.
    """
    fake = FakeDBStub()
    monkeypatch.setattr("src.message_service.main.get_db_stub", lambda: fake)
    return fake

def test_create_message_happy(patch_db_stub):
    from src.message_service import message_pb2

    fake_stub = patch_db_stub
    fake_response = message_pb2.Message(
        id=77, session_id=5, sender="u1", content="hello", context="ctx"
    )
    fake_stub.CreateMessage.return_value = fake_response

    servicer = MessageServiceServicer()
    req = message_pb2.CreateMessageRequest(
        session_id=5, sender="u1", content="hello", context="ctx"
    )
    resp = servicer.CreateMessage(req, ctx=None)

    fake_stub.CreateMessage.assert_called_once()
    called_req = fake_stub.CreateMessage.call_args[0][0]
    assert called_req.session_id == 5
    assert called_req.sender == "u1"
    assert called_req.content == "hello"
    assert called_req.context == "ctx"
    assert resp == fake_response

def test_list_messages_happy(patch_db_stub):
    from src.message_service import message_pb2

    fake_stub = patch_db_stub
    fake_response = message_pb2.MessageList(messages=[
        message_pb2.Message(id=1, session_id=2, sender="u2", content="c", context="ctx")
    ])
    fake_stub.ListMessages.return_value = fake_response

    servicer = MessageServiceServicer()
    req = message_pb2.ListMessagesRequest(session_id=2, skip=0, limit=10)
    resp = servicer.ListMessages(req, ctx=None)

    fake_stub.ListMessages.assert_called_once()
    called_req = fake_stub.ListMessages.call_args[0][0]
    assert called_req.session_id == 2
    assert called_req.skip == 0
    assert called_req.limit == 10
    assert resp == fake_response

def test_create_message_unhappy_db_raises(monkeypatch):
    from src.message_service import message_pb2

    fake_stub = MagicMock()
    fake_stub.CreateMessage.side_effect = grpc.RpcError("DB failure")
    monkeypatch.setattr("message_service.main.get_db_stub", lambda: fake_stub)

    servicer = MessageServiceServicer()
    req = message_pb2.CreateMessageRequest(session_id=123, sender="u", content="c", context="ctx")
    with pytest.raises(grpc.RpcError):
        _ = servicer.CreateMessage(req, ctx=None)

def test_list_messages_unhappy_db_raises(monkeypatch):
    from src.message_service import message_pb2

    fake_stub = MagicMock()
    fake_stub.ListMessages.side_effect = grpc.RpcError("DB fail")
    monkeypatch.setattr("message_service.main.get_db_stub", lambda: fake_stub)

    servicer = MessageServiceServicer()
    req = message_pb2.ListMessagesRequest(session_id=999, skip=0, limit=5)
    with pytest.raises(grpc.RpcError):
        _ = servicer.ListMessages(req, ctx=None)
