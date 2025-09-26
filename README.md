# Savannah_api

A Django REST API backend with PostgreSQL (via pg8000), Africa's Talking integration, and Google OIDC authentication.  
Deployment ready for **Railway** with **Docker** and **GitHub Actions CI/CD**.

---

 
savannah_api/ |-- core/                  # Local Django app (models, views, APIs) |   |-- migrations/        # Database migrations |   |-- init.py |   |-- admin.py |   |-- apps.py |   |-- models.py |   |-- serializers.py |   |-- tests.py |   -- views.py | |-- savannah_api/          # Main Django project folder |   |-- __init__.py |   |-- asgi.py |   |-- settings.py |   |-- urls.py |   -- wsgi.py | |-- templates/             # Templates (if needed for OIDC login) |-- staticfiles/           # Static assets (collected) |-- media/                 # Uploaded media files | |-- .env                   # Local environment variables |-- Dockerfile             # Docker container config |-- requirements.txt       # Dependencies |-- manage.py              # Django entrypoint |-- README.md              # Project documentation | -- .github/ -- workflows/ `-- ci-cd.yml      # GitHub Actions pipeline
---


##  Setup Instructions

### 1. Clone Repository
```bash
git clone https://github.com/<your-username>/Savannah_api.git
cd Savannah_api
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure `.env`
```
SECRET_KEY=your-django-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=savannah_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

AFRICASTALKING_USERNAME=your-username
AFRICASTALKING_API_KEY=your-api-key

# Optional Google OIDC (enable when deploying)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run Server
```bash
python manage.py runserver
```
Server runs at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

##  Running with Docker

### 1. Build Image
```bash
docker build -t savannah_api .
```

### 2. Run Container
```bash
docker run -d -p 8000:8000 --env-file .env savannah_api
```

---

##  Deployment on Railway

### 1. Install Railway CLI
```bash
npm i -g @railway/cli
```

### 2. Authenticate
```bash
railway login
```

### 3. Initialize project
```bash
railway init
```

### 4. Add PostgreSQL plugin
```bash
railway add postgres
```

### 5. Deploy
```bash
railway up
```

Railway will automatically read `.env` and build with `Dockerfile`.

---

##  Running Tests
```bash
python manage.py test
```

---

##  CI/CD (GitHub Actions)

The pipeline:
- Runs on pushes & PRs to **main**  
- Installs dependencies  
- Runs migrations & tests  
- Deploys to Railway if tests pass  

---

##  Example API Test
```bash
curl -X GET http://127.0.0.1:8000/api/health/
```

**Expected:**
```json
{"status": "ok"}
```

---