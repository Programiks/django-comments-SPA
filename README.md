# SPA Comments

A work-in-progress single-page application for posting and viewing threaded comments.

## Current stack

- Python 3.12
- Django 6.1
- Django ORM
- PostgreSQL 17
- Docker Compose

## Implemented foundation

- Django project and `comments` application
- PostgreSQL database running in Docker
- Environment-based database configuration
- Initial `Comment` model and migration
- Threaded comments through a self-referencing `parent` relation
- Required author name, email, optional home page, comment text, and attachment fields

## Local setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Create a local environment file from the template:

   ```powershell
   Copy-Item .env.example .env
   ```

4. Start PostgreSQL:

   ```powershell
   docker compose up -d
   ```

5. Apply database migrations:

   ```powershell
   python manage.py migrate
   ```

6. Run Django checks:

   ```powershell
   python manage.py check --database default
   ```

## Configuration

The project reads PostgreSQL settings from `.env`. The `.env` file must not be committed. Use `.env.example` as a template.

For the current local Docker setup, PostgreSQL is available at `localhost:5433`.

## Planned features

- REST API and SPA frontend
- CAPTCHA validation
- Safe HTML validation and XSS protection
- Image and TXT file validation
- Sorting and pagination
- AJAX preview and formatting toolbar
- WebSocket updates
- Full Dockerized application deployment