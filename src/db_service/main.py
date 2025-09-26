import os
from dotenv import load_dotenv
import grpc
from concurrent import futures
from sqlalchemy.orm import sessionmaker
from . import db_service_pb2, db_service_pb2_grpc
from .models import Base, ChatSession, Message, get_engine

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = get_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

class DBServiceServicer(db_service_pb2_grpc.DBServiceServicer):
    def CreateSession(self, req, ctx):
        db = SessionLocal(); s = ChatSession(name=req.name)
        db.add(s); db.commit(); db.refresh(s)
        return db_service_pb2.Session(id=s.id, name=s.name, is_favorite=s.is_favorite)
    def ListSessions(self, req, ctx):
        db = SessionLocal(); sessions = db.query(ChatSession).all()
        return db_service_pb2.SessionList(sessions=[db_service_pb2.Session(id=s.id,name=s.name,is_favorite=s.is_favorite) for s in sessions])
    def UpdateSession(self, req, ctx):
        db=SessionLocal(); s=db.query(ChatSession).get(req.id)
        if not s: ctx.abort(grpc.StatusCode.NOT_FOUND,'Not found')
        if req.name: s.name=req.name
        s.is_favorite=req.is_favorite
        db.commit(); return db_service_pb2.Session(id=s.id,name=s.name,is_favorite=s.is_favorite)
    def DeleteSession(self, req, ctx):
        db=SessionLocal(); s=db.query(ChatSession).get(req.id)
        if not s: ctx.abort(grpc.StatusCode.NOT_FOUND,'Not found')
        db.delete(s); db.commit(); return db_service_pb2.Empty()

    def CreateMessage(self, req, ctx):
        db=SessionLocal();
        if not db.query(ChatSession).get(req.session_id): ctx.abort(grpc.StatusCode.NOT_FOUND,'Session not found')
        m=Message(session_id=req.session_id,sender=req.sender,content=req.content,context=req.context)
        db.add(m); db.commit(); db.refresh(m)
        return db_service_pb2.Message(id=m.id,session_id=m.session_id,sender=m.sender,content=m.content,context=m.context)
    def ListMessages(self, req, ctx):
        db=SessionLocal(); msgs=db.query(Message).filter(Message.session_id==req.session_id).offset(req.skip).limit(req.limit).all()
        return db_service_pb2.MessageList(messages=[db_service_pb2.Message(id=m.id,session_id=m.session_id,sender=m.sender,content=m.content,context=m.context) for m in msgs])

def main():
    server=grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_service_pb2_grpc.add_DBServiceServicer_to_server(DBServiceServicer(), server)
    server.add_insecure_port('[::]:50050')
    print('DBService running on 50050')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    main()
