.PHONY: clean-migrations

PM=python3 manage.py

migrate:
	$(PM) makemigrations
	$(PM) migrate

admin:
	$(PM) createsuperuser

clean-migrations:
	find apps/ -path "*/migrations/*.py" ! -name "__init__.py" -delete
	rm -rf db.sqlite3

start:
	docker start redis_db

stop:
	docker start redis_db

check:
	docker exec -it redis_db redis-cli keys '*'
