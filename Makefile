.PHONY: init browser dump

init: .clean-venv .venv

.clean-venv:
	rm -rf .venv

.venv:
	pipx run poetry config virtualenvs.create true --local
	pipx run poetry install --sync

.venv-%: .venv
	poetry install --sync --only $*

# Create a container with a TOR browser
browser:
	docker run -d -p 5800:5800 domistyle/tor-browser

dump:
	docker exec -t postgres pg_dumpall -c -U user > dump.sql