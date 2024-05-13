# Vendor-Management-API

---

### Setup

Create a virtual environment

```bash
  python -m venv venv
```

Install dependencies

```bash
  pip install -r requirements.txt
```

1. Make Migrations

```bash
  python manage.py makemigrations
```

2. Migrate changes to database

```bash
  python manage.py migrate
```

3. Create a super user

```bash
  python manage.py createsuperuser
```

4. Run Server

```bash
  python manage.py runserver
```
