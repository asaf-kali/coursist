migrate:
	python manage.py makemigrations
	make black
	python manage.py migrate

black:
	black ./ -l 120