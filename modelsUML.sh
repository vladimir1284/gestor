source bin/activate
python manage.py graph_models utils users inventory equipment services costs -o models.png
python manage.py graph_models -a -I Order,Category,Transaction -o utils_models.png
python manage.py graph_models users -o users_models.png
python manage.py graph_models inventory -o inventory_models.png
python manage.py graph_models services -o services_models.png
python manage.py graph_models equipment -o equipment_models.png
python manage.py graph_models costs -o costs_models.png