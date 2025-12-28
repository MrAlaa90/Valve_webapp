### Quick context
- This repository is a Django (v5.2) web app for managing valves, spare parts, maintenance records and images.
- Project root apps: `valve_project/` (Django project settings & templates) and `valves/` (main app with models, views, serializers, management scripts).

### What matters for edits
- Views serve both HTML frontend and DRF APIs. See `valves/views.py` for patterns: class-based DRF views (e.g. `ValveList`, `ValveDetail`) alongside Django template views (e.g. `valve_detail_frontend`).
- Models are the canonical source of truth: `valves/models.py` (Valve, PartCode, MaintenanceHistory, MaintenancePart, ValveImage, etc.). Use `related_name` values (e.g. `maintenance_records`, `images`, `part_codes`) when loading related objects.
- Settings load environment variables from `.env` (via `python-dotenv`) and use `dj_database_url` to configure the DB (`valve_project/settings.py`). Respect `DEBUG` and `DATABASE_URL` env vars when adding code that depends on the DB.

### Key files to inspect before changing behavior
- `valves/models.py` — data model, verbose_names, translations (gettext_lazy).
- `valves/views.py`  — both API and frontend logic. Search for `Unified Search` logic using Django `Q` objects and `Subquery/OuterRef` for latest maintenance annotations.
- `valves/serializers.py` — DRF serialization; prefer explicit field lists.
- `valve_project/settings.py` — static/media paths, i18n setup (LANGUAGES includes `ar` and `en`), ngrok settings.
- `manage.py`, `pyproject.toml`, `requirements.txt` — environment and dependency hints.

### Project-specific conventions & patterns
- Mixed view styles: don't convert template views to APIs blindly; maintain separate endpoints for frontend templates and API consumers (see `ValveListFrontendView` vs `ValveList` DRF view).
- Explicit serializer fields: many serializers list explicit fields. Follow this pattern to avoid accidental field exposure.
- Translated strings: code uses gettext_lazy (`_`) extensively. Keep i18n context in mind when editing user-facing text.
- Image fields store under `MEDIA_ROOT = BASE_DIR / 'assets'` and upload paths use `upload_to` in models (e.g. `valve_images/`, `maintenance_images/`). Use Django file handling utilities when manipulating images.
- Search: Unified Search is implemented with `Q` objects across models (Valve fields, PartCode, MaintenancePart). Reuse the same strategy for new search features and keep pagination (Paginator) for results.

### Common developer workflows
- Local dev (typical): create & activate a virtualenv, install `requirements.txt`, set `.env` (SECRET_KEY, DEBUG=True, DATABASE_URL for sqlite or Postgres). Use `manage.py` to run server and migrations.
  - Example (Windows PowerShell):
    ```powershell
    python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt; copy db.sqlite3 db.sqlite3.bak
    $env:DEBUG='True'; python manage.py migrate; python manage.py runserver
    ```
- Tests: there are few or no automated tests in the repo. When adding behavior, add focused tests to `valves/tests.py` using Django TestCase and DRF APIClient for API endpoints.

### Safety & side-effects
- DB migrations: when changing models, create migrations (`python manage.py makemigrations`) and run them. Avoid destructive changes without migration strategy.
- Media files: operations that manipulate `MEDIA_ROOT` (`assets/`) can be large — avoid committing binary assets.

### Integration points & external deps
- Uses `dj_database_url` and `python-dotenv` to read DB and secrets from `.env`.
- Uses `whitenoise` for static files in production-like setups.
- REST endpoints use `djangorestframework`; API views require authentication (`IsAuthenticated`) in some endpoints (e.g. `upload_valve_images`). Respect permission classes when touching APIs.

### Examples (do this, not that)
- When loading a valve with related images and latest maintenance, prefer the existing approach in `valve_detail_frontend`:
  - valve = get_object_or_404(Valve.objects.prefetch_related('images'), pk=pk)
  - maintenance_records = valve.maintenance_records.all().order_by('-maintenance_date')
- For unified search across PartCode and Valve, reuse the Q-logic in `ValveListFrontendView.get` (look for `matching_part_codes` and `MaintenancePart` queries).
- For serializers, match the explicit field-list pattern (see `ValveSerializer`, `MaintenanceHistorySerializer`).

### Where to add tests & small improvements
- Add unit tests in `valves/tests.py`. Useful test targets: unified search, image upload API (`upload_valve_images`), and PartCode-Valve associations.
- Small low-risk improvements: add docstrings to complex view functions, fix minor typos, add pagination limits to APIs mirroring frontend limits.

### If you need to run migrations or tests in CI
- Use `python -m venv .venv` and `pip install -r requirements.txt`. Database in CI can be sqlite by setting `DATABASE_URL='sqlite:///db.sqlite3'` in env.

### Contact points in code
- Search for these symbols to find relevant behavior quickly:
  - `ValveListFrontendView`, `valve_detail_frontend`, `ValveSerializer`, `PartCode`, `MaintenanceHistory`, `upload_valve_images`.

If anything here is unclear or you want additional examples (tests, CI snippet, or migration guidelines), tell me which area to expand.

---

### تعليمات موجزة - النسخة العربية

- هذا المستودع هو تطبيق ويب مبني على Django (v5.2) لإدارة البلوف (valves)، وقطع الغيار، وسجلات الصيانة، والصور.
- التطبيقات الرئيسية: `valve_project/` (إعدادات المشروع والقوالب) و`valves/` (التطبيق الرئيسي يحتوي على النماذج، المشاهد، السيريالايزرز، وأوامر الإدارة).

### نقاط مهمة قبل التعديل
- تخدم المشاهد كلاً من الواجهات HTML وواجهات REST API. راجع `valves/views.py` لِمطَالعَة أنماط: مشاهد DRF (مثل `ValveList`, `ValveDetail`) إلى جانب مشاهد القالب (مثل `valve_detail_frontend`).
- النماذج (`valves/models.py`) هي المصدر الأساسي للبيانات: استعمل `related_name` الموجودة (مثل `maintenance_records`, `images`, `part_codes`) عند تحميل العلاقات.
- إعدادات المشروع تقرأ متغيرات البيئة من `.env` باستخدام `python-dotenv`، وتهيّئ قاعدة البيانات عبر `dj_database_url` (`valve_project/settings.py`). احترم متغيرات `DEBUG` و`DATABASE_URL` عند إضافة كود يعتمد على DB.

### قواعد وممارسات خاصة بالمشروع
- يوجد نمطان للمشاهد: واجهة مستخدم تعتمد على قوالب HTML وواجهات API منفصلة — لا تحول المشاهد القابعة في القوالب إلى API تلقائياً.
- يفضل تحديد الحقول صراحة في السيريالايزرز (انظر `valves/serializers.py`).
- النصوص القابلة للترجمة تُستخدم بكثافة (`gettext_lazy` أو `_`)؛ احفظ سياق i18n عند تعديل النصوص الموجهة للمستخدم.
- ملفات الوسائط تُخزن تحت `assets/` وحقول الصور تستخدم `upload_to` (مثال: `valve_images/`, `maintenance_images/`). تجنّب الالتزام بملفات باينارية كبيرة في Git.
- البحث الموحد مستخدم عبر `Q` objects و`Subquery/OuterRef` (انظر `ValveListFrontendView.get`). إعادة استخدام نفس النهج مقترحة.

### سير العمل (محلي)
- خطوات مختصرة (PowerShell):
  ```powershell
  python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
  $env:DEBUG='True'; python manage.py migrate; python manage.py runserver
  ```

### مخاوف الأمان والآثار الجانبية
- عند تعديل النماذج، أنشئ الميجرِيشِن المناسبة (`python manage.py makemigrations`) وقم بتطبيقها.
- العمليات التي تتعامل مع `MEDIA_ROOT` قد تكون مكلفة تخزينياً — لا تلتزم ملفات وسائط كبيرة داخل الريبو.

### أمثلة سريعة
- لتحميل بلف مع صوره وسجلات الصيانة الأخيرة استخدم نهج مشابه لـ `valve_detail_frontend`:
  - `get_object_or_404(Valve.objects.prefetch_related('images'), pk=pk)`
  - `valve.maintenance_records.all().order_by('-maintenance_date')`

### إذا أردت توسيع
- أستطيع إضافة مقاطع CI (GitHub Actions) لتشغيل الميجرِيشِن والاختبارات، أو إنشاء `AGENT.md` بمثال عملي: إضافة حقل نموذج + migration + serializer + اختبار.

أخبرني أي أجزاء إضافية تريد ترجمتها أو توسيعها.

