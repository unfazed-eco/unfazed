{{project_name}}
=====


## Quick Start


### Use Docker-Compose(recommended)

run {{ project_name }}

```bash

cd {{project_name}}/src/backend

docker-compose up -d 

docker-compose exec backend bash

# run command inside container
uvicorn asgi:application --host 0.0.0.0 --port 9527

# or
make run

```

### Use venv


```bash

cd {{project_name}}/src/backend


pip install uv

uv sync

# run command inside container
uvicorn asgi:application --host 0.0.0.0 --port 9527

# or
make run

```
