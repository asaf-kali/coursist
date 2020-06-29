#!/bin/bash

source ./env/bin/activate
python ./manage.py runcrons >>"$HOME"/logs/console.log 2>&1 &
