source ../gestorenv/bin/activate
python3 ../manage.py graph_models utils users inventory equipment services costs rent -o imgs/models.png
python3 ../manage.py graph_models -a -I Order,Category,Transaction -o imgs/utils_models.png
python3 ../manage.py graph_models users -o imgs/users_models.png
python3 ../manage.py graph_models inventory -o imgs/inventory_models.png
python3 ../manage.py graph_models services -o imgs/services_models.png
python3 ../manage.py graph_models equipment -o imgs/equipment_models.png
python3 ../manage.py graph_models costs -o imgs/costs_models.png
python3 ../manage.py graph_models rent -o imgs/rent_models.png