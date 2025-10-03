# Savannah API â€” Quick Start & Developer Guide

**Savannah API** is a Django REST backend that uses **PostgreSQL** for storage and integrates with **Africa's Talking** for SMS notifications. This guide focuses on what the project does, installation of the stack (Python, Django, PostgreSQL), required libraries and why they are needed, how to generate and secure the Django secret key, database setup (create DB, user, grant privileges), how to run and test the project locally (admin, APIs, add users, add customers/orders), how to test the SMS function, and how to run tests with coverage.

> This README focuses on *how to get the system running and tested locally*. It assumes a working Python environment and basic familiarity with the command line.

---

## What the project does (high level)

- Provides REST endpoints to manage **Customers** and **Orders**.
- When an Order is created the system can automatically send an SMS to the customer using **Africa's Talking**.
- Admin interface via Django admin for managing users, customers and orders.
- Authentication for API endpoints is handled via Django/DRF (session or basic auth).
- Tests and code coverage are provided.

---

## Prerequisites

### 1. Python
- **Recommended**: Python 3.10+.
- Install from https://www.python.org/downloads/ or using your platform package manager.

### 2. pip (Python package manager)
- `pip` typically comes bundled with Python.
- Upgrade pip:
```bash
python -m pip install --upgrade pip
```

### 3. Virtual environment (recommended)
Create and activate a virtualenv:

**Windows**
```powershell
python -m venv venv
.env\Scripts\activate
```

**Linux / macOS**
```bash
python -m venv venv
source venv/bin/activate
```

### 4. PostgreSQL
Install PostgreSQL (server + client tools).

- **Windows**: Download installer from https://www.postgresql.org/download/windows/ (pgAdmin and psql are included).
- **macOS**: Use Homebrew `brew install postgresql`.
- **Linux**: Use your distro package manager (`apt`, `dnf`, etc.), e.g. `sudo apt install postgresql postgresql-client`.

After installation ensure the `psql` CLI is on your `PATH`:
```bash
psql --version
```

---

## Required Python libraries (and what they do)

Install the libraries below (or put them into a `requirements.txt` file):

- `Django` â€” the web framework.
- `djangorestframework` â€” builds RESTful APIs (serializers, viewsets, routers).
- `psycopg2-binary` â€” PostgreSQL adapter (recommended for Windows / dev).
- `pg8000` â€” alternative pureâ€‘Python PostgreSQL adapter (optional).
- `python-dotenv` â€” load `.env` files into environment variables.
- `africastalking` â€” Africa's Talking SDK to send SMS.
- `social-auth-app-django` â€” Google OIDC / OAuth support (optional).
- `drf-yasg` â€” API docs (optional).
- `coverage` â€” test coverage measurement.

Example `requirements.txt`:
```
Django>=5.2
djangorestframework
psycopg2-binary
python-dotenv
africastalking
social-auth-app-django
drf-yasg
coverage
```

> On Linux servers, if compiling `psycopg2` is problematic you can use `pg8000` instead. Adjust Django `DATABASES` options accordingly.

---

## Generating a Django SECRET_KEY

**Method A â€” Django utility (recommended):**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the printed value into your `.env` as `SECRET_KEY=...`.

**Method B â€” Python:**
```python
import secrets
print(secrets.token_urlsafe(50))
```

**IMPORTANT:** Never commit the secret key to version control.

---

## Environment variables and `.env` template

Create a `.env` file at your project root (same folder as `manage.py`):

```ini
# Django
DEBUG=True
SECRET_KEY=replace_with_generated_secret

# PostgreSQL
DB_NAME=savannah
DB_USER=savannah_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Africa's Talking (sandbox during development)
AFRICASTALKING_USERNAME=sandbox
AFRICASTALKING_API_KEY=your_africastalking_api_key

# Google OIDC (optional)
GOOGLE_OIDC_CLIENT_ID=
GOOGLE_OIDC_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/oauth/callback/
```

Load `.env` in `settings.py` with `python-dotenv`.

---

## Database setup (PostgreSQL)

You only need to create the database and a user; Django handles tables with migrations.

### Using `psql`:

1. Connect as a superuser:
```bash
# Linux:
sudo -u postgres psql

# or if you have a password:
psql -U postgres -h localhost -p 5432
```

2. Run these SQL commands:

```sql
CREATE DATABASE savannah;
CREATE USER savannah_user WITH PASSWORD 'ChangeThisPassword';
GRANT ALL PRIVILEGES ON DATABASE savannah TO savannah_user;

-- Optional: connect to the DB and grant schema privileges:
\c savannah
GRANT USAGE, CREATE ON SCHEMA public TO savannah_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO savannah_user;
```

3. Exit:
```sql
\q
```

### Using pgAdmin (GUI)
- Create database `savannah`.
- Create login role `savannah_user` with password.
- Set privileges in the UI.

---

## `settings.py` â€” Database configuration examples

**Split variables (recommended for local dev):**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
        "OPTIONS": {},
    }
}
```

**Using `DATABASE_URL` + `dj-database-url`:**
```bash
pip install dj-database-url
```
```python
import os
import dj_database_url

DATABASES = {
    "default": dj_database_url.parse(os.getenv("DATABASE_URL"), conn_max_age=600)
}
```

**Important note about `driver` option**  
Do **not** add `"driver": "pg8000"` into the options when using `psycopg2`. Passing `driver` to `psycopg2` causes the error:
`invalid dsn: invalid connection option "driver"`. Only specify driver when necessary and matching your adapter.

---

## Installing dependencies

With virtualenv active:
```bash
pip install -r requirements.txt
```
or
```bash
pip install Django djangorestframework python-dotenv africastalking psycopg2-binary drf-yasg social-auth-app-django coverage
# Optionally:
pip install pg8000
```

---

## Run project locally

1. Activate venv.
2. Ensure `.env` exists and DB is created.
3. Install dependencies.
4. Run migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Start server:
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/admin/`.

---

## Admin: logging in & adding users

- Go to `http://127.0.0.1:8000/admin/`.
- Log in with the superuser.
- Add Django users, staff or superusers.
- Manage Customer and Order models from the admin.

---

## API: endpoints & testing

**Common endpoints (assuming `/api/` prefix)**:
- `GET /api/customers/` â€” list customers
- `POST /api/customers/` â€” create customer
- `GET /api/orders/` â€” list orders
- `POST /api/orders/` â€” create order (triggers SMS)
- `GET /api/test-sms/` â€” test sms endpoint (query param `phone`)

### Browsable API
- Visit endpoints in browser; login via the browsable UI (session auth).

### Example: Create a customer with curl (Basic Auth)
```bash
curl -u admin:adminpassword -X POST http://127.0.0.1:8000/api/customers/   -H "Content-Type: application/json"   -d '{"name":"Alice","phone_number":"+254700000000","email":"alice@example.com"}'
```

### Example: Create an order (and trigger SMS)
```bash
curl -u admin:adminpassword -X POST http://127.0.0.1:8000/api/orders/   -H "Content-Type: application/json"   -d '{"customer": 1, "item": "Widget", "amount": 1200}'
```

If you see `401/403` responses, either:
- Use the browsable UI to login first (session-based), or
- Add `BasicAuthentication` to your DRF settings (see earlier) or use a token-based auth.

---

## SMS integration: testing with Africa's Talking

**1) Sandbox setup**
- Set `AFRICASTALKING_USERNAME=sandbox`.
- Get sandbox API key from Africa's Talking dashboard.
- Add target phone numbers to sandbox recipients.

**2) Example `send_sms` helper**
```python
# core/utils.py
import os
import africastalking

username = os.getenv("AFRICASTALKING_USERNAME")
api_key = os.getenv("AFRICASTALKING_API_KEY")
africastalking.initialize(username, api_key)
sms = africastalking.SMS

def send_sms(to_number, message):
    return sms.send(message, [to_number])
```

**3) Test endpoint**
View in browser:
```
http://127.0.0.1:8000/api/test-sms/?phone=+2547XXXXXXXX
```
If you use the sandbox, check the Africa's Talking dashboard sandbox logs for messages.

---

## Tests & Coverage

### Run tests:
```bash
python manage.py test
```

### Run tests with coverage:
```bash
python -m coverage run manage.py test
python -m coverage report -m
python -m coverage html
```
Open the report:
```bash
# Windows
start htmlcov\index.html

# macOS / Linux
open htmlcov/index.html
```

### Mocking SMS in tests
Use `unittest.mock.patch` to mock `send_sms` so tests don't call external API:
```python
from unittest.mock import patch

@patch('core.utils.send_sms')
def test_create_order_triggers_sms(mock_send_sms):
    # create order...
    mock_send_sms.assert_called_once()
```

---

## Troubleshooting

- **`ModuleNotFoundError: No module named 'dj_database_url'`** â€” install `dj-database-url` if using `DATABASE_URL`.
- **`Invalid dsn: invalid connection option "driver"`** â€” remove `driver` from DB options when using `psycopg2`.
- **psycopg2 installation issues** â€” on Windows prefer `psycopg2-binary`. On Linux you may need `libpq-dev` and `python-dev` system packages to compile.
- **`404` on API routes** â€” ensure `core.urls` included in `savannah_api/urls.py`:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("core.urls")),
]
```

---
