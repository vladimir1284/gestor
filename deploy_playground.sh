#!/bin/bash

# Echo message for changing directory
echo "Changing directory to 'playground'..."
cd playground

# Echo message for pulling latest changes from git
echo "Pulling latest changes from git..."
git pull

# Echo message for activating virtual environment
echo "Activating virtual environment..."
source /home/vladimir/gestor/gestorenv/bin/activate

# Echo message for running database migration
echo "Running database migration..."
./manage.py migrate
./manage.py collectstatic

if [[ -z "$1" ]]; then
	echo "Please provide the sudo password as an argument."
	exit 1
fi

# Restart gunicorn service using systemctl with provided password
echo "$1" | sudo -S systemctl restart gunicorn_playground

# Check if the restart was successful
if [[ $? -eq 0 ]]; then
	echo "Gunicorn service has been restarted successfully."
else
	echo "Failed to restart Gunicorn service."
fi
