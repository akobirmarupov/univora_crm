from pathlib import Path
from datetime import timedelta
from decouple import config
import os
import dj_database_url

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-k3^@2garom%!df*-bkzl5rq9eu^nsxudm358h)xu6tlmfvaxf-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


AUTH_USER_MODEL = 'account.User'

# Application definition

DJANGO_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOCAL_APPS = [
    'account',
    'common',
    'crm',
]


EXTERNAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'rest_framework_simplejwt',
    'drf_yasg',
]



INSTALLED_APPS = DJANGO_APPS + EXTERNAL_APPS + LOCAL_APPS



ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


SWAGGER_SETTINGS = {
    'DEFAULT_API_URL': 'https://c87089dbf506e1bd-84-94-248.serveousercontent.com',
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
        }
    },
    'USE_SESSION_AUTH': False,
}

# Frontend ilova URL manzili (emaildagi tasdiqlash havolasi uchun)
FRONTEND_URL = "https://univora_crm.uz"


REST_FRAMEWORK = {
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'common.pagination.StandardPagination',
    'PAGE_SIZE': 10,

    # Throttling
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/min',       
        'user': '100/min',     
        'anon_burst': '20/min',  
        'auth_burst': '60/min',   
        'login': '5/min',      
        'register': '3/min',
    },

    # Autentifikatsiya
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],

    # Ruxsat (default)
    # 'DEFAULT_PERMISSION_CLASSES': [
    #     'rest_framework.permissions.IsAuthenticated',
    # ],
}


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",  # django.core.caches o'rniga
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}



UNFOLD = {
    "SITE_TITLE": "UNIVORA Admin",
    "SITE_HEADER": "UNIVORA",
    "SITE_SUBHEADER": "UNIVORA boshqaruv tizimi",
    "SITE_URL": "/",
    "SITE_SYMBOL": "univora_services",
    "BORDER_RADIUS": "16px",
    "THEME": "dark",
    "SITE_LOGO": {
        "light": "/static/images/logo.png",
        "dark": "/static/images/logo.png",
    },
    "STYLES": {
        "css": [
            lambda request: """
                html body div.flex.items-center.gap-4 img.unfold-logo,
                html body .unfold-sidebar header img,
                html body a[href="/admin/"] img {
                    width: 70px !important;
                    height: 70px !important;
                    object-fit: cover !important;
                    border-radius: 50% !important;
                    border: 3px solid #10b981 !important;
                    box-shadow: 0 0 15px rgba(16, 185, 129, 0.4) !important;
                    margin: 15px auto !important;
                    display: block !important;
                }
                html body div.flex.items-center.gap-4 .material-symbols-outlined {
                    display: none !important;
                }
                html body main .grid > div,
                html body main div[class*="shadow"] {
                    background-color: #1a2333 !important;
                    border: 2px solid #2e3b52 !important;
                    border-radius: 20px !important;
                    padding: 24px !important;
                    margin-bottom: 30px !important;
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3) !important;
                }
                html body main .grid > div table,
                html body main .grid > div div[class*="border-b"] {
                    background: #151c2c !important;
                    border-radius: 12px !important;
                    border: 1px solid #243146 !important;
                }
                html body div[class*="login"] img,
                html body .unfold-login-box img {
                    width: 130px !important;
                    height: 130px !important;
                    border-radius: 50% !important;
                    border: 4px solid #10b981 !important;
                    box-shadow: 0 0 25px rgba(16, 185, 129, 0.5) !important;
                    margin: 0 auto 30px auto !important;
                }
                html body .unfold-sidebar {
                    background-color: #0f141c !important;
                    border-right: 1px solid #1e293b !important;
                }
                html .unfold-sidebar-section-title {
                    color: #10b981 !important;
                    font-weight: 700 !important;
                    text-transform: uppercase !important;
                    letter-spacing: 0.05em !important;
                    border-left: 3px solid #10b981 !important;
                    padding-left: 10px !important;
                }
            """
        ],
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Asosiy Dashboard",
                "separator": True,
                "items": [
                    {"title": "Bosh sahifa", "icon": "space_dashboard", "link": "/admin/"},
                ],
            },
            {
                "title": "Foydalanuvchilar (Accounts)",
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": "Xodimlar (Users)", "icon": "group", "link": "/admin/account/user/"},
                ],
            },
            {
            "title": "CRM",
            "separator": True,
            "collapsible": False,
            "items": [
                {"title": "Kompaniyalar", "icon": "business", "link": "/admin/crm/company/"},
                {"title": "Kontaktlar", "icon": "person", "link": "/admin/crm/contact/"},
                {"title": "Bosqichlar (Stages)", "icon": "view_column", "link": "/admin/crm/stage/"},
                {"title": "Bitimlar (Deals)", "icon": "handshake", "link": "/admin/crm/deal/"},
                ],
            },
          
        ],
    },
}   