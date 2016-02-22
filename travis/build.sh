#!/usr/bin/env bash

#Exit on first error
set -e

#Usefull debugging information
sqlite3 -version

#Import all data
python manage.py test
time python manage.py sync_from_webservice
time python manage.py update_affair_details --parallel 12
