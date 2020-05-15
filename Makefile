migrate:
	python manage.py makemigrations
	make black
	python manage.py migrate

black:
	black ./ -l 120

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