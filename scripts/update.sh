git pull

crontab ./scripts/crontab_config.txt
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --no-input
python manage.py collectstatic --no-input

./scripts/run_server.sh
