proj
=====


## Quick Start


### Use Docker-Compose(recommended)

run proj

```bash

cd proj/src/backend

docker-compose up -d 

docker-compose exec backend bash

# run command inside container
python manage.py runserver --host 0.0.0.0 --port 9527

# or
make run

```

### Use venv


```bash

cd proj/src/backend


pip install uv

uv sync

# run command inside container
python manage.py runserver --host 0.0.0.0 --port 9527

# or
make run

```