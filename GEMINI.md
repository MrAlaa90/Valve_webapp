# Gemini Customization

This file helps Gemini understand your project's specific conventions and requirements.

## Project Overview

*   **Objective:** To manage valves, their associated data, and maintenance history.
*   **Technology Stack:** Python, Django 5.2.6, Django REST Framework, PostgreSQL (via `psycopg2-binary`), `dj_database_url`, `django-extensions`, `django-filter`, `crispy_forms`, `crispy_bootstrap5`, `djoser`.

## Conventions

*   **Coding Style:** Follows PEP 8 for Python.
*   **Commit Messages:** No specific convention found.
*   **Branching Strategy:** No specific convention found.

## Testing

*   **Framework:** Django's built-in `unittest` module (using `django.test.TestCase`).
*   **Test Location:** `tests.py` files within each Django app (e.g., `valves/tests.py`).
*   **Run Command:** `python manage.py test`