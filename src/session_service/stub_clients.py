import grpc, os
from . import db_service_pb2_grpc as db_grpc

def get_db_stub():
    channel = grpc.insecure_channel(os.getenv('DB_SERVICE_ADDR','db_service:50050'))
    return db_grpc.DBServiceStub(channel)