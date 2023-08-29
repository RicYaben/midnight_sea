.PHONY: init browser dump protos

init: .clean-venv .venv

.clean-venv:
	rm -rf .venv

.venv:
	pipx run poetry config virtualenvs.create true --local
	pipx run poetry install --sync

.venv-%: .venv
	pipx run poetry install --sync --only $*

# Create a container with a TOR browser
browser:
	docker run -d -p 5800:5800 domistyle/tor-browser

up:
	docker-compose -p ms -f bin/docker/docker-compose.yaml up -d --build

dump:
	docker exec -t postgres pg_dumpall -c -U user > dump.sql

docker-db:
	docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_USER=username -e POSTGRES_DB=midnight_sea -d -p 5432:5432 postgres

protos:
	@python -m grpc_tools.protoc \
	--proto_path=lib/src/lib/protos=bin/protos \
	--python_out=. \
	--grpc_python_out=. \
	bin/protos/*.proto