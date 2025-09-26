.PHONY: proto build up

proto:
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/db_service --grpc_python_out=./src/db_service src/proto/db_service.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/session_service --grpc_python_out=./src/session_service src/proto/session.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/session_service --grpc_python_out=./src/session_service src/proto/db_service.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/message_service --grpc_python_out=./src/message_service src/proto/message.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/message_service --grpc_python_out=./src/message_service src/proto/db_service.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/api_gateway --grpc_python_out=./src/api_gateway src/proto/session.proto
	python3 -m grpc_tools.protoc -I src/proto --python_out=./src/api_gateway --grpc_python_out=./src/api_gateway src/proto/message.proto

build: proto
	docker-compose build

up: build
	docker-compose up
