# SPA Comments

A work-in-progress Django application for posting and viewing threaded comments.

The project is being developed step by step from a server-rendered Django interface toward the SPA requirements of the test assignment.

## Current stack

- Python 3.12
- Django 6.1
- Django ORM
- PostgreSQL 17
- Docker Compose
- Bleach for safe HTML sanitization

## Implemented features

- Django project and `comments` application
- PostgreSQL database running in Docker
- Environment-based database configuration
- `Comment` model with a self-referencing `parent` relation
- Required author name and email fields
- Optional home page field
- Comment text field
- Attachment field prepared for future file upload support
- Creation of top-level comments through a browser form
- Rendering of top-level comments on the main page
- Creation of replies to any comment at any nesting level
- Recursive rendering of unlimited nested comment replies
- Automated tests for comment creation, HTML validation, and nested replies
- Nested-reply test coverage for multiple comment levels
- Default newest-first comment ordering
- Sorting controls for top-level comments by author name, email, and creation date
- Ascending and descending sorting directions
- Pagination with 25 top-level comments per page
- Nested reply threads preserved within each paginated top-level comment
- Basic CSS layout for the form and comment cards
- Safe HTML validation for comment text
- Allowed HTML tags: `a`, `code`, `i`, and `strong`
- Safe link protocols: `http`, `https`, and `mailto`

## Current limitations

The following features are planned but not implemented yet:

- CAPTCHA validation
- Image and TXT file upload validation and processing
- Client-side validation
- AJAX comment preview
- HTML formatting toolbar
- REST API and SPA frontend
- WebSocket updates
- Full Dockerized application deployment

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

7. Start the development server:

   ```powershell
   python manage.py runserver
   ```

8. Open the application:

   ```text
   http://127.0.0.1:8000/
   ```

## Configuration

The project reads PostgreSQL settings from `.env`.

Do not commit `.env`. Use `.env.example` as a configuration template.

For the current local Docker setup, PostgreSQL is available at:

```text
localhost:5433
```

## Comment rules

- `author_name` is required and may contain only Latin letters and digits.
- `email` is required and must have a valid email format.
- `home_page` is optional and must be a valid URL when provided.
- `text` is required.
- Comment HTML is restricted to `a`, `code`, `i`, and `strong`.
- Only `href` and `title` attributes are allowed for `a` tags.
- Link protocols are restricted to `http`, `https`, and `mailto`.