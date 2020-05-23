install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	python manage.py migrate

run:
	python manage.py runserver

black:
	black ./ -l 120

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

com:
	make black
	git add .
	git commit -m "Auto commit"
	git push