# tests/test_db_service.py

import os
import pytest
import grpc
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db_service.models import Base, ChatSession, Message
from src.db_service.main import DBServiceServicer

# Fake gRPC context that raises RpcError on abort()
class FakeContext:
    def abort(self, code, details):
        raise grpc.RpcError(details)


@pytest.fixture(scope="module")
def sqlite_in_memory_db(tmp_path_factory, monkeypatch):
    """
    Create a temporary SQLite file and point DATABASE_URL to it.
    """
    db_file = tmp_path_factory.mktemp("db") / "test_db.sqlite"
    db_url = f"sqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", db_url)

    # Create tables in that SQLite file
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)

    # Provide SessionLocal factory
    SessionLocal = sessionmaker(bind=engine)
    yield SessionLocal

    # Teardown: drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_service_servicer(sqlite_in_memory_db):
    """
    Instantiate DBServiceServicer (which reads DATABASE_URL from env).
    """
    servicer = DBServiceServicer()
    return servicer


def test_create_session_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    req = db_service_pb2.CreateSessionRequest(name="Test Session")
    resp = db_service_servicer.CreateSession(req, ctx=None)

    assert resp.id > 0
    assert resp.name == "Test Session"

    # Verify via SQLAlchemy
    SessionLocal = sqlite_in_memory_db
    db = SessionLocal()
    stored = db.query(ChatSession).filter_by(id=resp.id).one()
    assert stored.name == "Test Session"


def test_list_sessions_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    # Create a second session
    create_req = db_service_pb2.CreateSessionRequest(name="Another Session")
    _ = db_service_servicer.CreateSession(create_req, ctx=None)

    list_resp = db_service_servicer.ListSessions(db_service_pb2.Empty(), ctx=None)
    assert len(list_resp.sessions) >= 2
    names = [s.name for s in list_resp.sessions]
    assert "Test Session" in names and "Another Session" in names


def test_update_session_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    create_req = db_service_pb2.CreateSessionRequest(name="ToBeUpdated")
    create_resp = db_service_servicer.CreateSession(create_req, ctx=None)

    update_req = db_service_pb2.UpdateSessionRequest(
        id=create_resp.id, name="UpdatedName", is_favorite=True
    )
    update_resp = db_service_servicer.UpdateSession(update_req, ctx=None)

    assert update_resp.id == create_resp.id
    assert update_resp.name == "UpdatedName"
    assert update_resp.is_favorite is True

    # Verify via SQLAlchemy
    SessionLocal = sqlite_in_memory_db
    db = SessionLocal()
    sess = db.query(ChatSession).get(create_resp.id)
    assert sess.name == "UpdatedName"
    assert sess.is_favorite is True


def test_update_session_unhappy_not_found(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    fake_ctx = FakeContext()
    update_req = db_service_pb2.UpdateSessionRequest(
        id=9999, name="DoesNotExist", is_favorite=False
    )
    with pytest.raises(grpc.RpcError):
        _ = db_service_servicer.UpdateSession(update_req, ctx=fake_ctx)


def test_delete_session_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    create_req = db_service_pb2.CreateSessionRequest(name="ToBeDeleted")
    create_resp = db_service_servicer.CreateSession(create_req, ctx=None)

    delete_req = db_service_pb2.SessionId(id=create_resp.id)
    delete_resp = db_service_servicer.DeleteSession(delete_req, ctx=None)
    assert delete_resp is not None

    SessionLocal = sqlite_in_memory_db
    db = SessionLocal()
    assert db.query(ChatSession).get(create_resp.id) is None


def test_delete_session_unhappy_not_found(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    fake_ctx = FakeContext()
    delete_req = db_service_pb2.SessionId(id=12345)
    with pytest.raises(grpc.RpcError):
        _ = db_service_servicer.DeleteSession(delete_req, ctx=fake_ctx)


def test_create_message_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    # Create a session first
    create_sess_req = db_service_pb2.CreateSessionRequest(name="ForMessage")
    session_resp = db_service_servicer.CreateSession(create_sess_req, ctx=None)

    create_msg_req = db_service_pb2.CreateMessageRequest(
        session_id=session_resp.id,
        sender="user1",
        content="Hello",
        context="ctx-1"
    )
    msg_resp = db_service_servicer.CreateMessage(create_msg_req, ctx=None)
    assert msg_resp.id > 0
    assert msg_resp.session_id == session_resp.id
    assert msg_resp.sender == "user1"
    assert msg_resp.content == "Hello"

    # Verify via SQLAlchemy
    SessionLocal = sqlite_in_memory_db
    db = SessionLocal()
    stored = db.query(Message).filter_by(id=msg_resp.id).one()
    assert stored.content == "Hello"


def test_create_message_unhappy_session_not_found(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    fake_ctx = FakeContext()
    create_msg_req = db_service_pb2.CreateMessageRequest(
        session_id=99999, sender="u", content="Hi", context="ctx"
    )
    with pytest.raises(grpc.RpcError):
        _ = db_service_servicer.CreateMessage(create_msg_req, ctx=fake_ctx)


def test_list_messages_happy(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    create_sess_req = db_service_pb2.CreateSessionRequest(name="ForListing")
    session_resp = db_service_servicer.CreateSession(create_sess_req, ctx=None)

    # Create three messages
    for i in range(3):
        create_msg_req = db_service_pb2.CreateMessageRequest(
            session_id=session_resp.id,
            sender=f"user{i}",
            content=f"msg{i}",
            context=f"ctx{i}"
        )
        _ = db_service_servicer.CreateMessage(create_msg_req, ctx=None)

    list_req = db_service_pb2.ListMessagesRequest(
        session_id=session_resp.id, skip=1, limit=1
    )
    list_resp = db_service_servicer.ListMessages(list_req, ctx=None)
    assert len(list_resp.messages) == 1
    m = list_resp.messages[0]
    assert m.sender == "user1" and m.content == "msg1"


def test_list_messages_unhappy_no_session(sqlite_in_memory_db, db_service_servicer):
    from db_service import db_service_pb2

    list_req = db_service_pb2.ListMessagesRequest(
        session_id=88888, skip=0, limit=10
    )
    list_resp = db_service_servicer.ListMessages(list_req, ctx=None)
    assert list_resp.messages == []
