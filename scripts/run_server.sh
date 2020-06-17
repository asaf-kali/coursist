cd "$HOME"/ || exit 1
source env/bin/activate

echo "Killing server..."
pkill -f runserver

echo "Starting server..."
python manage.py runserver 0.0.0.0:5000 >>runserver.log 2>&1 &
echo "Server is running"

tail -f runserver.log
