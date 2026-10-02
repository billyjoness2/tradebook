# tradebook

A small backend service with a REST API, built with Django and Django REST Framework as a learning project.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
copy .env.example .env        # then set DJANGO_SECRET_KEY (cp on macOS/Linux)
python manage.py migrate
python manage.py runserver
```
