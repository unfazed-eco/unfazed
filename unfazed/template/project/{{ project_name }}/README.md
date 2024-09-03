{{project_name}}
=====


## Quick Start

run {{ project_name }}

```bash

cd {{project_name}}/src/backend

docker-compose up -d 

docker-compose exec backend bash

# run command inside container

python manage.py init-db
python manage.py runserver --host 0.0.0.0 --port 9527


```



mkdocs

```bash

# run command inside container
# becareful with the port number, now same as backend, change it if you need
mkdocs serve 0.0.0.0:9527

```