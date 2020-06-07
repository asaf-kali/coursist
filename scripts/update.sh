cd "$HOME"/coursist/ || exit 1
source env/bin/activate

git pull
pip install -r requirements.txt
python manage.py migrate

./scripts/run_server.sh
