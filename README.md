# Gestor

This is a custom ERP for a small trailer repair and rental business.

## Models

See data base design in the [docs](docs/models.md).

## Como instalar el proyecto:

Descargarlo:
git clone https://github.com/vladimir1284/gestor.git

tener instalado la version del python >=3.10 
cambiar para el directorio del proyecto:
 cd my_project

copiar los archivos .json, y squlite que se descargan de la pagina, .env, al mismo nivel del manage.py:
 - token.json
 - trailer-rental-323614-d43be7453c41.json
 - .env
 - db.sqlite3

Se puede descargar del:

http://towithouston.com/erp/db.sqlite3
https://towithouston.com/backups/

Luego crear un entorno virtual: 
pip install virtualenv
virtualenv venv
\venv\Scripts\activate.bat

ejecutar en ese entorno virtual el requirements.txt:
pip install -r requirements.txt


luego revisar que las dependecias y biblioteca esten correctas.
despues:
python manage.py createsuperuser
python manage.py runserver