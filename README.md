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
- Pillow for CAPTCHA image generation
- Lightbox2 for image attachment previews
- Django cache framework (LocMemCache)

## Implemented features

- Django project and `comments` application
- PostgreSQL database running in Docker
- Environment-based database configuration
- `Comment` model with a self-referencing `parent` relation
- Required author name and email fields
- Optional home page field
- Comment text field
- File attachments for comments
- Allowed attachment formats: JPG, GIF, PNG, and TXT
- Image validation and proportional resizing to a maximum of 320×240 pixels
- TXT file validation with a maximum size of 100 KB
- Inline image attachment rendering
- Lightbox2 image preview
- TXT attachment links
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
- Rendering of server-validated allowed HTML in comments
- Client-side validation for comment text length
- Client-side attachment validation for allowed file extensions
- Client-side TXT attachment size validation up to 100 KB
- Styled client-side and server-side form validation errors
- Server-side CAPTCHA generation with Pillow
- CAPTCHA image validation using the Django session
- CAPTCHA input field with readable generated code
- HTML formatting toolbar with `[i]`, `[strong]`, `[code]`, and `[a]` buttons
- Client-side insertion of allowed HTML tags via toolbar
- AJAX comment preview with server-side HTML sanitization
- Preservation of line breaks in newly created comments
- JWT-based authentication (in phase 2):
  - User registration and login via REST API (`/api/auth/register/`, `/api/auth/login/`);
  - JWT access/refresh tokens using djangorestframework-simplejwt;
  - Token stored in localStorage and sent with requests;
  - UI with login/register modal, automatic form prefill for logged-in users;
  - Restricted image attachments:
    - non-authenticated users cannot upload files;
    - non-authenticated users do not see image attachments in comments.
- **Cache for comment list (in phase 2):**
  - Django cache framework (`django.core.cache`) with `LocMemCache` backend;
  - Server-side caching of comment list queries based on page, sort field, and direction;
  - Cache invalidation on new comment creation via `cache.clear()`.
- **Events for comment creation (in phase 2):**
  - Django signals (`post_save` on `Comment` model);
  - `comment_created` event logged on every new comment;
  - Decoupled event handling ready for future extensions (emails, queues, analytics).
- **Comment queue (in phase 2):**
  - New comments are not published immediately.
  - They are saved to the database with `status = "pending"` and become visible only after the queue is processed.
  - Queue processing happens automatically after each request via middleware.
  - This setup can be easily replaced with a background worker (e.g. Celery) without changing the core logic.
- **Real-time comment updates via WebSocket (in phase 2):**
  - Django Channels (`channels`) for WebSocket support;
  - `comment_created` event broadcast to all connected clients when a new comment is published;
  - Client-side JavaScript handles incoming events and updates the comment list without page reload;
  - In-memory channel layer (`InMemoryChannelLayer`) for development; can be replaced with Redis for production.

## Phase 1: Backend-first implementation

All features listed above were initially implemented entirely on the backend using Django. This phase demonstrates server-side capabilities:

- Full form handling and validation in Django.
- Server-side CAPTCHA generation and verification.
- File upload handling with image resizing and TXT size validation.
- Nested comments with recursive rendering.
- Sorting and pagination of root comments.
- Server-side HTML sanitization and allowed-tag enforcement.
- AJAX preview with server-side rendering.

At the end of Phase 1, the application was fully functional with server-rendered templates and minimal JavaScript.

## Phase 2: Vue frontend enhancement

The second phase enhances the existing Django application with Vue 3. The backend remains the source of truth for validation, security, and persistence.

Implemented Vue features:

- Reactive form state managed with `v-model`.
- Client-side validation:
  - User Name is required and accepts only Latin letters and digits;
  - E-mail is required and checked for a basic email format;
  - Home page is optional and checked as an HTTP/HTTPS URL;
  - CAPTCHA is required on the client; its actual value is verified on the server;
  - comment text is checked for length, allowed tags, and tag pairing;
  - attachments are checked for allowed file types and TXT size.
- Instant validation-error display without page reload.
- AJAX comment preview without page reload.
- HTML tag toolbar: `[i]`, `[strong]`, `[code]`, `[a]`.
- Removal of the legacy JavaScript implementation in favor of Vue.


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
   http://127.0.0.1:8000/comments/
   ```

## Configuration

The project reads PostgreSQL settings from `.env`.

Do not commit `.env`. Use `.env.example` as a configuration template.

Uploaded attachments are stored locally in `attachments/` and are ignored by Git.

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

## Running Tests

To run the comment system tests:

```bash
python manage.py test comments.tests
```

### Test Coverage

- **CommentCreationTest**: Basic comment creation with valid data
- **CommentEmailValidationTest**: Email validation (required, format)
- **CommentTextLengthValidationTest**: Text length constraints (2–2000 characters)
- **CommentCaptchaValidationTest**: CAPTCHA validation (placeholder)
- **CommentHtmlValidationTest**: HTML sanitization and XSS prevention
- **NestedCommentsTest**: Unlimited nested comment replies

## 🐳 Docker Deployment

The project can be deployed using Docker Compose with a single command.

### Prerequisites

- Docker installed
- Docker Compose installed

### Quick Start

1. Clone the repository:

```bash
git clone <your-repo-url>
cd <project-folder>
```

2. Create `.env` file from template:

```bash
cp .env.example .env
```

3. Build and start containers:

```bash
docker-compose up --build
```

4. Open the application:

```text
http://localhost:8000/comments/
```

### Docker Configuration

- **PostgreSQL 15**: Database service on port 5433
- **Django**: Web application on port 8000
- **Volumes**: Database data persists in `postgres_data` volume

### Stop Containers

```bash
docker-compose down
```

### Rebuild After Changes

```bash
docker-compose up --build
```

---

## 📊 Database Schema

See `database_schema.sql` file for MySQL Workbench compatible schema.

---
