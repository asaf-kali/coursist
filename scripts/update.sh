cd "$HOME"/coursist/ || exit 1
source env/bin/activate

git pull
pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input

./scripts/run_server.sh
