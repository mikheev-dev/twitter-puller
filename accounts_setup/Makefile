setup-local:
# 	docker run --name psql -e POSTGRES_USER=bgt -e POSTGRES_PASSWORD=bigten -e POSTGRES_DB=tweets  -p 5432:5432 -d postgres
# 	sleep 20
	python3 ./setup.py

local-restart:
	docker rm -f psql
	docker run --name psql -e POSTGRES_USER=bgt -e POSTGRES_PASSWORD=bigten -e POSTGRES_DB=tweets  -p 5432:5432 -d postgres
	sleep 20
	python3 ./setup.py

down-local:
	docker rm -f psql
