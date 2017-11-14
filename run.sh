#!/bin/bash

if [ "$1" = "app" ]
then
	python3 app/app_application.py $2
else
    python3 app/app_blockchain.py $2
fi