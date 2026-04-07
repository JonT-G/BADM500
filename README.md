# BADM500 — Video Sharing Platform

A YouTube-style video sharing platform built with Django, SQLite, plain CSS/HTML and implemented with activitypub (yet to do) 

## Running the app

```bash
python run.py
```

Installs dependencies, runs migrations, and starts the server in one step.

- Site: **http://127.0.0.1:8080**
- Admin panel: **http://127.0.0.1:8080/admin/**

Or with Docker:

```bash
docker-compose up --build
```

## Test data

The `test_data/` folder contains scripts to populate the database with test users, videos, and interactions for testing features.

Run everything at once:

```bash
python test_data/test_all.py
```

Or run individual tests:

```bash
python test_data/test_users.py         # creates test users
python test_data/test_videos.py        # creates test videos
python test_data/test_interactions.py  # likes, comments, subscriptions
python test_data/test_notifications.py # notifications
```

Test login credentials after running:

| Username | Password   | Role      |
|----------|------------|-----------|
| admin    | admin123   | Superuser |
| alice    | alice123   | User      |
| bob      | bob123     | User      |
| charlie  | charlie123 | User      |

## Tech

Backend: Django 5, Python 3.11. Database: SQLite. Frontend: Django templates, plain CSS.
