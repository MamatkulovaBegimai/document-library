# Китепкана — Django версиясы

Мурунку Node.js/Express версиясынын Django'го которулган түрү. Django Templates
колдонулат — башкача айтканда, бүт нерсе серверде түзүлүп, даяр HTML катары
жөнөтүлөт (өзүнчө JS-фронтенд же API талап кылынбайт).

## Мүмкүнчүлүктөр

- Издөө (аталышы, автору, сүрөттөмө, тегдер боюнча)
- Категория боюнча чыпкалоо, барактоо (pagination)
- Файл жүктөө (PDF/DOCX) — жөнөкөй форма аркылуу
- Ар бир документ үчүн өзүнчө бет жана жүктөп алуу эсеби
- **Django admin** — `/admin/` аркылуу документтерди башкаруу (издөө,
  чыпкалоо, түзөтүү) кошумча код жазбай эле иштейт
- Файл сактоо катмары `.env` аркылуу which жергиликтүү дискиден
  AWS S3 / Cloudflare R2'ге которулат (кодду өзгөртүүнүн кереги жок)

## Талаптар

- Python 3.11+

## Орнотуу жана иштетүү

```bash
cd document_library_django
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser   # admin панели үчүн (милдеттүү эмес)
python manage.py runserver
```

Андан кийин:
- Сайт: **http://127.0.0.1:8000/**
- Admin панели: **http://127.0.0.1:8000/admin/**

> **Эскертүү:** мен бул долбоорду жазган чөйрөмдө интернет жок болгондуктан,
> `pip install` жана `runserver`'ди иш жүзүндө иштетип көрө алган жокмун.
> Бардык Python файлдарынын синтаксисин текшердим (`py_compile` менен), бирок
> биринчи ирет өзүңүздө иштеткенде кичине каталар чыгып калса (мисалы, версия
> дал келбестиктери), айтыңыз — токтоосуз оңдойм.

## Долбоордун түзүлүшү

```
document_library_django/
├── manage.py
├── config/                # Долбоордун жалпы орнотуулары
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── library/                # Негизги тиркеме (app)
│   ├── models.py           # Document модели
│   ├── forms.py            # Жүктөө формасы
│   ├── views.py             # Тизме, деталь, жүктөө, upload
│   ├── urls.py
│   ├── admin.py             # Django admin катталышы
│   ├── templates/library/
│   │   ├── base.html
│   │   ├── document_list.html
│   │   ├── document_detail.html
│   │   └── document_upload.html
│   └── static/library/css/style.css
├── media/                  # Жүктөлгөн файлдар (local режиминде)
├── data/                    # SQLite base файлы
└── requirements.txt
```

## Cloud storage'го (S3 / Cloudflare R2) которуу

1. Орнотуу:
   ```bash
   pip install django-storages boto3
   ```
2. `requirements.txt` ичинде эки сапты комментарийден чыгаруу.
3. `.env` файлында:
   ```
   STORAGE_PROVIDER=r2
   S3_BUCKET=document-library
   S3_REGION=auto
   S3_ENDPOINT=https://<account-id>.r2.cloudflarestorage.com
   S3_ACCESS_KEY_ID=...
   S3_SECRET_ACCESS_KEY=...
   ```
   `settings.py`'де бул баалуулуктар эбак эле окулат — эч нерсени кол менен
   өзгөртүүнүн кереги жок.

## Node.js версиясынан айырмасы

| | Node.js/Express версиясы | Django версиясы |
|---|---|---|
| Frontend | Өзүнчө JS (fetch, fetch API) | Django Templates (server-rendered) |
| Base | SQLite + FTS5 (кол менен түзүлгөн) | SQLite + Django ORM |
| Admin панель | Жок (өзүнчө жазылышы керек эле) | Даяр (`/admin/`) |
| Издөө | Толук текст (FTS5) | `icontains` (жөнөкөй, base-агностик) |

Эгер каалаган учурда JSON API кайра керек болсо (мисалы, мобилдик колдонмо
үчүн), Django REST Framework кошуп, учурдагы моделдерди өзгөртпөй эле API
кабатын кошсо болот.

## Деплой кылуу

Render, Railway, PythonAnywhere, же VPS (Gunicorn + Nginx) сыяктуу каалаган
Python/Django колдогон платформага деплой кылса болот. Продакшндо:
- `DJANGO_DEBUG=False` коюу
- `DJANGO_SECRET_KEY`'ди кокустук маанилүү сапка алмаштыруу
- `python manage.py collectstatic` иштетүү
- SQLite ордуна PostgreSQL колдонуу сунушталат (эгер бир нече серверде иштетсеңиз)
