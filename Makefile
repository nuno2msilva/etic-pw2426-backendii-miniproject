up: setup db-init

setup:
	docker compose up --build

down:
	docker compose down -v

db-init:
	docker compose exec db psql -U postgres -d postgres -c \
		"CREATE TABLE IF NOT EXISTS records ( \
		  id SERIAL PRIMARY KEY, \
		  name VARCHAR NOT NULL, \
		  age INTEGER NOT NULL, \
		  email VARCHAR NOT NULL, \
		  location VARCHAR NOT NULL \
		);"

seed:
	docker compose exec db psql -U postgres -d postgres -c \
		"INSERT INTO records (name, age, email, location) VALUES ('nuno', 30, 'nuno_silva@eticalgarve.com', 'faro');"

rows:
	docker compose exec db psql -U postgres -d postgres -c \
		"SELECT * FROM records ORDER BY id;"