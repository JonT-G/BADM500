# BADM500 — Video Sharing Platform

A YouTube-style video sharing platform built with Django, SQLite, plain CSS/HTML. Implemented with activitypub protocol. 

## Running the app

```bash
python run.py
```

Installs dependencies, runs migrations, and starts the server in one step.

- Site: **http://127.0.0.1:8080**
- Admin panel: **http://127.0.0.1:8080/admin/**
- Pbulic URL: **https://hardwood-mortified-stump.ngrok-free.dev**

One normal account was premade:
username: bob
password: bobbobbob123!

and a superuser:
username: admin
password: admin123

## Tech

Backend: Django 5, Python 3.11. Database: SQLite. Frontend: Django templates, plain CSS.


## To test that it is connected to the fediverse the following websites can be used (ngrok and app needs to be running):
    - https://activitypub.academy
    - https://browser.pub
For activitypub academy you make a account, it make one random and in the search bar you type "@alice@hardwood-mortified-stump.ngrok-free.dev" and it will pub up and you can follow and stuff. you can then check with the activity log at right handside for more information. 
For Broser.pub which is a fediverse explorer which handles and it fetches and renders raw JSON in easy to read format (not really needed since activitypub.academy is enough) but in searchbar you do: "https://hardwood-mortified-stump.ngrok-free.dev/users/alice".

