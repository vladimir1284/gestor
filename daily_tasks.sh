#!/bin/bash

cd /home/vladimir/gestor/

source gestorenv/bin/activate

./manage.py shell < rent/send_invoices.py

