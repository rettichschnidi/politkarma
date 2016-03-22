#!/usr/bin/env bash

#Exit on first error
set -e

#Usefull debugging information
sqlite3 -version

#Import all data
python manage.py test
python manage.py sync_from_webservice
python manage.py update_affair_details --parallel 12
python manage.py load_test_organizations
