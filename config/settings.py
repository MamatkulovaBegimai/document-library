"""
Django settings for document_library_django долбоору.
"""
import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-insecure-secret-key-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [h.strip() for h in os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h.strip()]

# Render сыяктуу платформаларда HTTPS'тин артында иштегенде CSRF үчүн керек.
# Мисалы: https://document-library.onrender.com
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'library',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'library.context_processors.library_context',
            ],
        },
    },
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'library:document_list'
LOGOUT_REDIRECT_URL = 'library:document_list'

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Базасы: DATABASE_URL коюлса — ошол (мисалы, Render'дин PostgreSQL'и).
# Коюлбаса — жергиликтүү иштетүү үчүн SQLite (data/db.sqlite3).
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'data' / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Bishkek'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'library' / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# ---- Файлдарды сактоо ----
# Демейки: жергиликтүү диск. Cloud storage'го которуу үчүн README.md караңыз.
STORAGE_PROVIDER = os.getenv('STORAGE_PROVIDER', 'local')

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# whitenoise: статикалык файлдарды кысылган жана кэштелүүчү түрдө берет,
# өзүнчө CDN же nginx керек эмес.
_STATICFILES_BACKEND = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

if STORAGE_PROVIDER in ('s3', 'r2'):
    # pip install django-storages boto3 (requirements.txt'де бар)
    STORAGES = {
        'default': {'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage'},
        'staticfiles': {'BACKEND': _STATICFILES_BACKEND},
    }
    AWS_ACCESS_KEY_ID = os.getenv('S3_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('S3_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('S3_BUCKET')
    AWS_S3_REGION_NAME = os.getenv('S3_REGION', 'auto')
    AWS_S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT')  # R2 үчүн милдеттүү
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None
    AWS_S3_CUSTOM_DOMAIN = os.getenv('S3_PUBLIC_DOMAIN')  # R2 публикалык домен коюлса (милдеттүү эмес)
else:
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': _STATICFILES_BACKEND},
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Жүктөлүүчү файлдын максималдуу өлчөмү (100 MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024

# ---- Email / сырсөздү калыбына келтирүү ----
# Продакшнда SMTP параметрлерин Render Environment'те бериңиз.
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG
    else 'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', '')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@example.com')

# Render (жана окшош платформалар) TLS'ти reverse proxy'де аяктайт да,
# ички трафикти HTTP аркылуу жөнөтөт. Ушул сап болбосо, Django суракты
# HTTP катары кабыл алып, CSRF/redirect каталарын берет.
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
