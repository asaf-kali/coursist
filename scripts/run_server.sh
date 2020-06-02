export LD_LIBRARY_PATH="/usr/local/lib"

source ./env/bin/activate

python manage.py runserver 0.0.0.0:5000
