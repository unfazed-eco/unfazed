{{project_name}}
=====


## Quick Start

```bash

cd {{project_name}}/src/backend

docker-compose up -d 

docker-compose exec unfazed bash

# run command inside container

python manage.py init-db
python manage.py runserver --host 0.0.0.0 --port 8000


```