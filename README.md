# BADM500 - Video Sharing Platform
A YouTube-style video sharing platform built with **Django** and **SQLite**. Interactivity is with Python or with CSS.

## Tech Stack
| Layer | Technology |
|-------|-----------|
| Backend | Django 5.2 (Python 3.11) |
| Database | SQLite |
| Frontend | Django templates + CSS |
| Auth | Django built-in auth |
| Container | Docker |

## Quick Start
```bash
#
# Install dependencies
pip install django

# Apply database migrations
python manage.py migrate

# (Optional) Load sample data
python manage.py shell < seed_data.py

# Start the server
python manage.py runserver 8080
```

Visit **http://127.0.0.1:8080**

### Docker (alternative)

```bash
# Build and start
docker-compose up --build

# Or run detached
docker-compose up --build -d
```

The container runs migrations automatically on startup.

## Sample Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |
| maria | testpass123 | User |
| jake | testpass123 | User |
| sarah | testpass123 | User |
| tom | testpass123 | User |
| lisa | testpass123 | User |
| kevin | testpass123 | User |
| emma | testpass123 | User |
| nina | testpass123 | User |

## Project Structure

```
├── badm500/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── videos/             # Main Django app
│   ├── models.py       # Video, Comment, Like, Subscription
│   ├── views.py        # All page views + actions
│   ├── forms.py        # Upload, Register forms
│   ├── urls.py         # URL routing
│   └── admin.py        # Admin panel config
├── templates/          # Django HTML templates
│   ├── base.html       # Base layout (nav, sidebar)
│   ├── index.html      # Home / search / video grid
│   ├── watch.html      # Video player + comments
│   ├── upload.html     # Upload form
│   ├── profile.html    # User profile + tabs
│   ├── login.html      # Login form
│   └── register.html   # Registration form
├── static/css/         # CSS modules
│   ├── style.css       # Main (imports all modules)
│   ├── base.css        # Variables, reset, buttons
│   ├── nav.css         # Navigation + sidebar
│   ├── videos.css      # Video grid + player
│   ├── forms.css       # Forms + auth pages
│   ├── profile.css     # Profile page
│   └── responsive.css  # Media queries
├── media/              # Uploaded video files
├── Dockerfile          # Docker image definition
├── docker-compose.yml  # Docker orchestration
├── requirements.txt    # Python dependencies
├── .dockerignore
├── manage.py
├── seed_data.py        # Database seeder
└── db.sqlite3          # SQLite database
```

## Features

- **User auth** — Register, login, logout (Django auth)
- **Video upload** — Upload videos with title, description, visibility (public/unlisted/private)
- **Watch page** — Video player, like/dislike, subscribe, comments
- **Profiles** — User pages with video grid, stats, about tab
- **Search** — Filter videos by title/description via `?q=` parameter on the home page
- **YouTube-style sidebar** — CSS-only collapsible sidebar (checkbox hack, no JS)
- **Dark theme** — Responsive design with CSS custom properties
- **Admin panel** — Full Django admin at `/admin/`

- **Sidebar toggle:** CSS checkbox hack (`input:checked ~ .sidebar`)
- **Profile tabs:** Server-side via query parameter (`?tab=videos` / `?tab=about`)
- **Search:** Standard HTML form GET to `/?q=`
- **Comments, likes, subscribe:** HTML form POST to Django views
- **Flash messages:** Django messages framework with CSS animations
- **Form validation:** Django server-side validation + HTML5 `required` attribute
