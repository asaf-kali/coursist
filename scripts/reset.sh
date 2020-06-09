cd "$HOME"/coursist/ || exit 1
source env/bin/activate

pip freeze | grep -v -f requirements.txt - | grep -v '^#' | xargs pip uninstall -y
pip install -r requirements.txt
