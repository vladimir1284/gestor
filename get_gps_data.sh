#!/bin/bash

# Echo message for changing directory 
echo "Changing directory to 'gestor'..." 
cd /home/vladimir/gestor 
 
# Echo message for activating virtual environment 
echo "Activating virtual environment..." 
source gestorenv/bin/activate 
 
# Echo message for running data request 
echo "Running data request..." 
./manage.py shell < utility_scripts/get_tracker_data.py  
