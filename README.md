
![unfazed](docs/images/unfazed-title.png)

<p align="center">
    <em>Production Ready ASGI web framework</em>
</p>


-----

**Documentation**: [unfazed](https://unfazed-eco.github.io/)

-----


Unfazed
----

Unfazed is a production-oriented ASGI web framework focused on building enterprise-grade applications. 100% test coverage, with a robust architecture inspired by Django, it provides high performance、scalability、maintainability、testability web application.


Unfazed offers powerful features:

Core Features:
- pluggable app system
- Built-in command line interface
- Flexible middleware system
- Robust ORM with Tortoise-ORM integration
- Caching for high performance
- Lifespan protocol support

API Development:
- Focus only on correct business logic
- Full OpenAPI/Swagger support
- Serializer framework built on Tortoise-ORM
- Request argument parsing and validation
- Comprehensive test client
- Static files service

Security & Sessions:
- Role-based access control (RBAC)
- Secure session management
- Production-ready admin interface


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
unfazed-cli startapp -n myapp

```


3. runserver

```shell

uvicorn asgi:application --host 0.0.0.0 --port 9527

```

4. follow tutorial

[unfazed-tutorial](https://unfazed-eco.github.io/)


