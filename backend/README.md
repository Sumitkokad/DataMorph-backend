# Project Structure

This document outlines the file structure of the Django backend project.

```
backend/
├── db.sqlite3
└── mainproject/
    ├── __init__.py
    ├── asgi.py
    ├── manage.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── mainapp/
        ├── __init__.py
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── tests.py
        ├── urls.py
        ├── views.py
        ├── logic/
        │   ├── llm_logic.py
        │   └── preprocessing_routes.py
        ├── migrations/
        │   └── __init__.py
        └── operations/
            ├── Encoding.py
            ├── Outlier.py
            └── Scaling.py
```

## Description

- **backend/**: Root directory of the backend project.
  - **db.sqlite3**: SQLite database file.
  - **mainproject/**: Main Django project directory.
    - Standard Django project files: `__init__.py`, `asgi.py`, `manage.py`, `settings.py`, `urls.py`, `wsgi.py`.
    - **mainapp/**: Main Django app.
      - Standard Django app files: `__init__.py`, `admin.py`, `apps.py`, `models.py`, `tests.py`, `urls.py`, `views.py`.
      - **logic/**: Directory for business logic modules.
        - `llm_logic.py`: Logic related to LLM (Large Language Model).
        - `preprocessing_routes.py`: Routes for preprocessing operations.
      - **migrations/**: Database migrations.
      - **operations/**: Directory for data operation modules.
        - `Encoding.py`: Encoding operations.
        - `Outlier.py`: Outlier handling.
        - `Scaling.py`: Scaling operations.
