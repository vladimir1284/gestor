#!/bin/bash

# Remove old migrations
rm ./*/migrations/*.py

# Init migrations folder as python modules
for e in */migrations; do
	touch "$e/__init__.py"
done

# Migrate django defaults to the new database
# python manage.py migrate
# Generate new cleans migrations
# python manage.py makemigrations
# Migrate the new database
# python manage.py migrate

# Save old data
python manage.py dumpdata --database=old_db -o data.json
# python manage.py dumpdata --exclude=contenttypes --database=old_db >data.json

# Clear new DB
python manage.py flush --noinput
# Apply migrations and data to new DB
python manage.py shell <./utility_scripts/db_mig_sqlite_to_postgres.py
# Load data to the new DB
# python manage.py loaddata data.json
