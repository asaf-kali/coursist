source ./env/bin/activate

export LD_LIBRARY_PATH="/usr/local/lib"
export COURSIST_ENV="prod"

python manage.py runserver 0.0.0.0:5000
