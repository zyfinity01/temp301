# Web Server

## Development

First, create the dev database:

```shell
python3 manage.py migrate
```

then seed the DB with some dev values:

```shell
python3 manage.py runscript seed_db
```

`runscript` is an addon provided by the `django-extensions` package.

Next, create a super user:

```shell
python3 manage.py createsuperuser --email admin@example.com --username admin
```

## TODOs

- [ ] Use HyperlinkedModelSerializers propely
- [ ] Don't use device ID as primary key - it breaks stuff
