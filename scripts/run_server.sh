cd "$HOME"/coursist/ || exit 1
source env/bin/activate

python manage.py runserver 0.0.0.0:5000 >>runserver.log 2>&1 &
echo "Server is running"
tail -f server.log
