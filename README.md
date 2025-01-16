
![unfazed](docs/images/unfazed-title.png)

<p align="center">
    <em>Production Ready ASGI web framework</em>
</p>


-----

**Documentation**: [unfazed](https://unfazed.github.io/)

-----


Unfazed
----


Unfazed is a fully-featured ASGI web framework that is production ready. It is designed to build fast, scalable, maintainable web applications and inspired by Django.


Unfazed offer you

- pluggable app system
- command system
- middleware
- tortoise-orm integration
- redis cache integration
- process safe log handler
- lifespan protocol
- openapi support
- serializer support based on tortoise-orm
- scalable admin page with unfazed-admin(coming soon)
- basic rbac system
- session support
- test client support
- request args parser support


and with unfazed ecosystem

- unfazed-admin
- unfazed-prometheus
- unfazed-celery
- unfazed-sentry
- unfazed-redis
- unfazed-locust
- unfazed-pyroscope
- unfazed-scalene ?

with these tools, you can build a production-ready web application quickly.


## Installation

```shell

pip install unfazed


```

## Quick start

1、create a new project

```shell
unfazed-cli startproject -n myproject

cd myproject/src/backend

docker-compose up -d
docker-compose exec unfazed bash


```

2. create a new app

```shell

# add app to project
python manage.py startapp -n myapp

```


3. runserver

```shell

python manage.py runserver --host 0.0.0.0 --port 9527

```

4. follow toturial

[unfazed-tutorial](https://unfazed.github.io/)


