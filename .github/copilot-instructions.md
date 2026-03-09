# BADM500 - Video Sharing Platform

## Project Overview
A YouTube-style video sharing platform built with Django and SQLite.
No JavaScript — all interactivity is handled server-side or with pure CSS.

## Tech Stack
- **Backend:** Django 5.2 (Python 3.11)
- **Database:** SQLite (built-in)
- **Frontend:** HTML templates + CSS (no JavaScript)
- **CSS Architecture:** Modular CSS with @import (base, nav, videos, forms, profile, responsive)

## Project Structure
- `badm500/` — Django project settings
- `videos/` — Main Django app (models, views, forms, urls, admin)
- `templates/` — Django HTML templates (base.html + page templates)
- `static/css/` — CSS modules
- `media/` — User-uploaded video files

## Running the Project
```
python manage.py runserver 8080
```
Visit http://127.0.0.1:8080

### Docker (alternative)
```
docker-compose up --build
```

## Key Features
- User registration/login (Django auth)
- Video upload with title, description, visibility
- Video watch page with comments, likes, related videos
- User profiles with video grid and stats
- Search functionality
- YouTube-style sidebar (CSS-only toggle)
- Responsive dark theme
- Django admin panel at /admin/

## Sample Accounts
- Admin: `admin` / `admin123`
- Users: `maria`, `jake`, `sarah`, `tom`, `lisa`, `kevin`, `emma`, `nina` (all passwords: `testpass123`)

- Work through each checklist item systematically.
- Keep communication concise and focused.
- Follow development best practices.
