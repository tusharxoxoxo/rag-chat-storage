from concurrent import futures
import os
from dotenv import load_dotenv
import grpc
from . import message_pb2_grpc, db_service_pb2, db_service_pb2_grpc

def get_db_stub():
    channel = grpc.insecure_channel(os.getenv('DB_SERVICE_ADDR', 'db_service:50050'))
    return db_service_pb2_grpc.DBServiceStub(channel)

load_dotenv()
db_stub = get_db_stub()

class MessageServiceServicer(message_pb2_grpc.MessageServiceServicer):
    def CreateMessage(self, req, ctx):
        return db_stub.CreateMessage(db_service_pb2.CreateMessageRequest(session_id=req.session_id, sender=req.sender, content=req.content, context=req.context))
    def ListMessages(self, req, ctx):
        return db_stub.ListMessages(db_service_pb2.ListMessagesRequest(session_id=req.session_id, skip=req.skip, limit=req.limit))

def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    message_pb2_grpc.add_MessageServiceServicer_to_server(MessageServiceServicer(), server)
    server.add_insecure_port('[::]:50052')
    print('MessageService running on port 50052')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    main()