# Run Activityhub

Use these commands from the project root (`/home/mathan/projects/Activityhub`).

## 1) Run `manage.py`

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py
```

This prints available Django subcommands.

## 2) Start the Django server

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Then open: `http://127.0.0.1:8000`

If you see `Error: That port is already in use.`, use one of these:

```bash
# Run on a different port
/home/mathan/projects/Activityhub/.venv/bin/python manage.py runserver 127.0.0.1:8001

# Or find and stop the process using 8000
ss -ltnp | grep ':8000'
kill <PID>
```

## 3) Common commands

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py migrate
/home/mathan/projects/Activityhub/.venv/bin/python manage.py createsuperuser
/home/mathan/projects/Activityhub/.venv/bin/python manage.py test
```

## 4) After Hosting: Add or Remove Admin

Run these commands on your hosted server (or inside your app container/shell).

### Add a new admin (interactive)

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py createsuperuser
```

### Make an existing user admin

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

u = User.objects.get(username="example_user")
u.is_staff = True
u.is_superuser = True
u.save()
```

### Remove admin access (keep user account)

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

u = User.objects.get(username="example_user")
u.is_staff = False
u.is_superuser = False
u.save()
```

### Delete an admin user completely

```bash
/home/mathan/projects/Activityhub/.venv/bin/python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

User.objects.filter(username="example_user").delete()
```
