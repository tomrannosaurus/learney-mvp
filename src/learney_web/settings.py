"""Django settings for learney_web project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
from pathlib import Path

import yaml

import sentry_sdk
from mixpanel import Mixpanel
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://bc60f04d032e4ea590973ebc6d8db2f5@o1080536.ingest.sentry.io/6086500",
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
    # By default the SDK will try to use the SENTRY_RELEASE
    # environment variable, or infer a git commit
    # SHA as release, however you may want to set
    # something more human-readable.
    # release="myapp@1.0.0",
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open("dev_env.yaml", "r") as env_file:
    dev_secrets_dict = yaml.load(env_file, Loader=yaml.Loader)

DT_STR = "%d/%m/%Y, %H:%M:%S"

SECRET_KEY = dev_secrets_dict["SECRET_KEY"]

SLACK_TOKEN = dev_secrets_dict["SLACK_TOKEN"]
NOTION_KEY = dev_secrets_dict["NOTION_KEY"]
AWS_CREDENTIALS = dev_secrets_dict["AWS_CREDENTIALS"]
PYTHON_ENV = os.environ.get("PYTHON_ENV", "dev")
assert PYTHON_ENV in ["dev", "staging", "production"]

mixpanel = Mixpanel(dev_secrets_dict["MIXPANEL_KEY"])

FRONTEND_URL = dev_secrets_dict["FRONTEND_URL"][PYTHON_ENV]
IS_PROD = PYTHON_ENV == "production"

ALLOWED_HOSTS = [
    # prod
    "api.learney.me",
    "learneyapp-env.eba-ed9hpad3.us-west-2.elasticbeanstalk.com",
    "172.31.8.139",
    "172.31.13.26",
    # staging
    "staging-api.learney.me",
    "staging-learneybackend-env.us-west-2.elasticbeanstalk.com",
    "172.31.39.124",
    "172.31.18.129",
    "44.233.38.189",
    # dev
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
]

# Log output to a log file stored in the container
DEBUG_PROPAGATE_EXCEPTIONS = True
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "formatters": {
#         "verbose": {
#             "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
#             "datefmt": "%d/%b/%Y %H:%M:%S",
#         },
#         "simple": {"format": "%(levelname)s %(message)s"},
#     },
#     "handlers": {
#         "file": {
#             "level": "DEBUG",
#             "class": "logging.FileHandler",
#             "filename": "learney.log",
#             "formatter": "verbose",
#         },
#     },
#     "loggers": {
#         "django": {
#             "handlers": ["file"],
#             "propagate": True,
#             "level": "DEBUG",
#         },
#         "MYAPP": {
#             "handlers": ["file"],
#             "level": "DEBUG",
#         },
#     },
# }

# Application definition

INSTALLED_APPS = [
    "corsheaders",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "social_django",
    "button_presses",
    "learney_backend",
    "goals",
    "knowledge_maps",
    "learned",
    "link_clicks",
    "page_visits",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "learney_web.urls"

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

WSGI_APPLICATION = "learney_web.wsgi.application"

CORS_ORIGIN_WHITELIST = (FRONTEND_URL,)
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "cache-control",
    "content-type",
    "dnt",
    "origin",
    "sentry-trace",
    "x-csrftoken",
    "x-requested-with",
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

if "RDS_DB_NAME" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": os.environ["RDS_DB_NAME"],
            "USER": os.environ["RDS_USERNAME"],
            "PASSWORD": os.environ["RDS_PASSWORD"],
            "HOST": os.environ["RDS_HOSTNAME"],
            "PORT": os.environ["RDS_PORT"],
        }
    }
else:
    DATABASES = {"default": dev_secrets_dict["DATABASES"]}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Set to use HTTPS if on production server
if PYTHON_ENV in ["production", "staging"]:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 518400
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# For auth0
with open("auth0_conf.yaml", "r") as auth0_conf_file:
    auth0_conf = yaml.load(auth0_conf_file, Loader=yaml.Loader)
