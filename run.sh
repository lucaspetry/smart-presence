#!/bin/bash

if [ "$1" = "app" ]
then
	export FLASK_APP=app/app.py
else
    export FLASK_APP=blockchain/app.py
fi

flask run --host=0.0.0.0 --port="$2"