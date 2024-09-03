Unfazed
=====

async only python web framework, still in development


```bash

pip install unfazed

unfazed-cli startproject -n myproject

cd myproject/src/backend

docker-compose up -d
docker-compose exec backend bash

# run command inside container

make run

# add app to project
python manage.py startapp -n myapp

```