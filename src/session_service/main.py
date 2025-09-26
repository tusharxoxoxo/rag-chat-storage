import os
from concurrent import futures

import grpc
from dotenv import load_dotenv

from . import db_service_pb2
from . import db_service_pb2_grpc
from . import session_pb2_grpc


def get_db_stub():
    channel = grpc.insecure_channel(os.getenv('DB_SERVICE_ADDR', 'db_service:50050'))
    return db_service_pb2_grpc.DBServiceStub(channel)

load_dotenv()
db_stub = get_db_stub()

class SessionServiceServicer(session_pb2_grpc.SessionServiceServicer):
    def CreateSession(self, req, ctx):
        return db_stub.CreateSession(db_service_pb2.CreateSessionRequest(name=req.name))
    def ListSessions(self, req, ctx):
        return db_stub.ListSessions(db_service_pb2.Empty())
    def UpdateSession(self, req, ctx):
        return db_stub.UpdateSession(db_service_pb2.UpdateSessionRequest(id=req.id, name=req.name, is_favorite=req.is_favorite))
    def DeleteSession(self, req, ctx):
        return db_stub.DeleteSession(db_service_pb2.SessionId(id=req.id))

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    session_pb2_grpc.add_SessionServiceServicer_to_server(SessionServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    print('SessionService running on port 50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    main()
