#!/bin/bash

if [ "$1" = "app" ]
then
	export FLASK_APP=app/app_application.py
else
    export FLASK_APP=app/app_blockchain.py
fi

flask run --host=0.0.0.0 --port="$2"