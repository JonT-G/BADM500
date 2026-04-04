# BADM500 — Video Sharing Platform using ActivityPub

A YouTube-style video sharing platform built with Django, CSS, HTML, SQLite and ActivityPub.

## Running the app

The simplest way is `python run.py`, it installs dependencies, runs migrations, and starts the server in one step.

```bash
python run.py
```

Or with Docker, when running multiple instances for federation testing:

```bash
docker-compose up --build
```

The site: **http://127.0.0.1:8080**

## Project structure

```
badm500/          Django project config (settings, urls, wsgi)
videos/
  models.py       Database tables (Video, Comment, Like, Subscription, etc.)
  views/          Page views split by responsibility
    pages.py      index, watch, upload, profile
    auth.py       register, login, logout
    actions.py    like, subscribe, save, vote
    library.py    history, watch later, liked videos, notifications
  forms.py        Upload, register, and profile forms
  urls.py         URL routing
  streaming.py    HTTP Range support so video seeking works
  admin.py        Django admin panel config
templates/
  base.html       Shared layout: nav, sidebar, flash messages
  includes/       Reusable partials: video_grid, comment, avatar
  *.html          One file per page
static/css/       CSS split by concern (nav, videos, forms, profile, responsive)
db/db.sqlite3     SQLite database
media/            Uploaded video and image files
```

## Tech

Backend is Django 5 with Python 3.11. Database is SQLite. Frontend is Django templates and plain CSS.
