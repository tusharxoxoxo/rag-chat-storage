import grpc
import os
from . import session_pb2_grpc, message_pb2_grpc

def get_session_stub():
    channel = grpc.insecure_channel(os.getenv('SESSION_SERVICE_ADDR', 'session_service:50051'))
    return session_pb2_grpc.SessionServiceStub(channel)

def get_message_stub():
    channel = grpc.insecure_channel(os.getenv('MESSAGE_SERVICE_ADDR', 'message_service:50052'))
    return message_pb2_grpc.MessageServiceStub(channel)
