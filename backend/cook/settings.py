import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', default='token')

DEBUG = os.getenv('DEBUG') == 'True'
# DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # "debug_toolbar",
    'rest_framework',
    'django_filters',
    "rest_framework.authtoken",
    "djoser",
    "kitchen.apps.KitchenConfig",
    "api.apps.ApiConfig",
    "users.apps.UsersConfig",

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# INTERNAL_IPS = [
#     "127.0.0.1",
# ]

ROOT_URLCONF = "cook.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cook.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'foodgram'),
        'USER': os.getenv('POSTGRES_USER', 'foodgram_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'ulfsnftmhg'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'DB_PORT': os.getenv('DB_PORT', '5432'),
    }
}

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

DJOSER = {
    'LOGIN_FIELD': 'email',
}

AUTH_USER_MODEL = 'users.User'

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework.authentication.SessionAuthentication'
    ],
    'SEARCH_PARAM': 'name',
}

DJOSER = {
    'LOGIN_FIELD': 'email',
    'SERIALIZERS': {
        'user': 'api.serializers.CustomUserSerializer',
        'current_user': 'api.serializers.CustomUserSerializer',
    },
    'PERMISSIONS': {
        'user': ['rest_framework.permissions.AllowAny'],
        'current_user': ['rest_framework.permissions.IsAuthenticated'],
        'user_list': ['rest_framework.permissions.AllowAny'],
    },
    'HIDE_USERS': False,
}

LENGTH_LIMITS = {
    'user_email': 254,
    'user_first_name': 150,
    'user_password': 150,
    'ingredient_name': 60,
    'ingredient_measurement_unit': 30,
    'tag_name': 50,
    'tag_color': 7,
    'tag_slug': 50,
    'recipe_name': 200
}

PAGE_SIZE = 6
