.PHONY: up down browser dump destroy

# Put the container up
up: 
	@docker-compose -p midnight_sea -f deployments/docker-compose.yaml up -d --build

# Put the container down
down:
	@docker-compose -p midnight_sea -f deployments/docker-compose.yaml down

destroy:
	@docker-compose -p midnight_sea -f deployments/docker-compose.yaml down -v

# Create a container with a TOR browser
browser:
	docker run -d -p 5800:5800 domistyle/tor-browser

dump:
	docker exec -t postgres pg_dumpall -c -U user > dump.sql