install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	python manage.py migrate
	python manage.py dev_init
	python manage.py fetch_courses --limit 20

run:
	python manage.py runserver

black:
	black . -l 120 --exclude ".*/node_modules/.*"

migrate:
	python manage.py makemigrations
	make black
	python manage.py migrate

pull:
	python scripts/gits.py pull

push:
	python scripts/gits.py push

rebase:
	python scripts/gits.py rebase

prod:
	source env/bin/activate
	pip install -r requirements.txt
	python manage.py migrate

com:
	git add .
	git status
	git commit -m "Auto commit"
	git push