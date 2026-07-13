# FocusFlow Task Tracker

A full-stack task tracker built with React, Vite, FastAPI, and SQLAlchemy.

## Features

- Create, edit, complete, search, and delete tasks
- Categories, priorities, and optional due dates
- Progress dashboard and task filtering
- Responsive React interface
- SQLite for local development and PostgreSQL support for production

## Run locally

Start the API:

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Start the frontend in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173` and the API is available at `http://localhost:8000`.

A new login/signup flow is available, and task operations now use JWT authentication to keep each user’s tasks private.

## Deploy on Render

This repository includes `render.yaml`, which provisions a FastAPI web service, a Vite static site, and a PostgreSQL database. During the Render Blueprint setup, provide:

- `CORS_ORIGINS`: the public frontend URL
- `VITE_API_URL`: the public backend URL
