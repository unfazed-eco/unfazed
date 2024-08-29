{{project_name}}
=====


## Quick Start

```bash

cd {{project_name}}/src/backend

docker-compose up -d 

docker-compose exec {{project_name}} bash

# run command inside container

python manage.py init-db
python manage.py runserver 0:80


```