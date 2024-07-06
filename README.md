# ERP/CRM Backend

This project is meant to be an all-purpose take on enterprise management software that allows for 
complete customization of its capabilities and what it will measure. Making it a very flexible asset
for enterprises that are in need of a management platform.

The current project represents the backend, and should be ran concurrently with the frontend. In order to set up the frontend,
check out the [frontend project repository]().

## Project setup

To configure the project, the following is needed:

### Install dependencies

#### Docker

You need to have the docker engine installed in order to run this project.

### Configure database and .env file

The `.env` file should include the following variables:

* DJANGO_SECRET_KEY
* DJANGO_DEBUG
* DB_NAME
* DB_USER
* DB_PASSWORD
* DB_HOST
* DB_PORT
* DJANGO_SENDER_EMAIL
* DJANGO_SENDER_EMAIL_PASSWORD
* FRONT_END_BASE_URL
* REDIS_PRIVATE_URL

Once the database is set, run the following commands:

```
python manage.py makemmigrations
```

```
python manage.py migrate
```

### Run server

```
docker compose up --build
```
