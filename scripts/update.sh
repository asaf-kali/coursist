cd "$HOME"/ || exit 1
git pull

source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input

./scripts/run_server.sh
