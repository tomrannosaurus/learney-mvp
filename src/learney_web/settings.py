"""Django settings for learney_web project.

Generated by 'django-admin startproject' using Django 3.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import json
import os
from pathlib import Path

import requests
import yaml

import sentry_sdk
from learney_web.utils import get_concept_names, get_prerequisite_dict, retrieve_map_from_s3
from mixpanel import Mixpanel
from sentry_sdk.integrations.django import DjangoIntegration

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

with open("dev_env.yaml", "r") as env_file:
    dev_secrets_dict = yaml.load(env_file, Loader=yaml.Loader)

DT_STR = "%d/%m/%Y, %H:%M:%S"

SECRET_KEY = dev_secrets_dict["SECRET_KEY"]

SLACK_TOKEN = dev_secrets_dict["SLACK_TOKEN"]
NOTION_KEY = dev_secrets_dict["NOTION_KEY"]
MIXPANEL_KEY = dev_secrets_dict["MIXPANEL_KEY"]
AWS_CREDENTIALS = dev_secrets_dict["AWS_CREDENTIALS"]
PYTHON_ENV = os.environ.get("PYTHON_ENV", "dev")
assert PYTHON_ENV in ["dev", "staging", "production"]

mixpanel = Mixpanel(MIXPANEL_KEY)

with open("link_preview_api_key.yaml", "r") as secrets_file:
    LINK_PREVIEW_API_KEY = yaml.load(secrets_file, Loader=yaml.Loader)["API_KEY"]

IS_PROD = PYTHON_ENV == "production"

CONTENT_JSON = json.loads(
    retrieve_map_from_s3(
        s3_bucket_name="learney-prod" if IS_PROD else "learney-test",
        s3_key="questions_map.json",
        aws_credentials=AWS_CREDENTIALS,
    )
)

QUESTIONS_PREREQUISITE_DICT = get_prerequisite_dict(CONTENT_JSON)
CONCEPT_NAMES = get_concept_names(CONTENT_JSON)

if PYTHON_ENV in ["staging", "production"]:
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

ALLOWED_HOSTS = [
    ".amazonaws.com",
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
try:
    EC2_TOKEN = requests.put(
        "http://169.254.169.254/latest/api/token",
        timeout=0.5,
        headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
    ).text
    EC2_IP = requests.get(
        "http://169.254.169.254/latest/meta-data/local-ipv4",
        headers={
            "X-aws-ec2-metadata-token-ttl-seconds": "21600",
            "X-aws-ec2-metadata-token": EC2_TOKEN,
        },
    ).text
    ALLOWED_HOSTS.append(EC2_IP)
except requests.exceptions.ReadTimeout:
    EC2_IP = requests.get("http://169.254.169.254/latest/meta-data/local-ipv4").text
    ALLOWED_HOSTS.append(EC2_IP)
except requests.exceptions.RequestException:
    pass

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
    # "social_django",
    "accounts",
    "button_presses",
    "learney_backend",
    "goals",
    "knowledge_maps",
    "learned",
    "link_clicks",
    "page_visits",
    # "silk",
    "questions",
    "rest_framework",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # "silk.middleware.SilkyMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

# SILKY_PYTHON_PROFILER = True
# SILKY_PYTHON_PROFILER_BINARY = True
# SILKY_PYTHON_PROFILER_RESULT_PATH = "../silk_profiler_results"
# SILKY_AUTHENTICATION = True  # User must login
# SILKY_AUTHORISATION = True  # User must have permissions
# # (by default Silk will only authorise users with is_staff==True)
# # Set SILKY_PERMISSIONS to determine who can be authorised
# # You can use a lambda. E.g.
# # SILKY_PERMISSIONS = lambda user: user.is_superuser
# SILKY_META = True  # Tracks the effect Silk has on request/response time

if dev_secrets_dict["FRONTEND_URL"][PYTHON_ENV] != "*":
    CORS_ORIGIN_WHITELIST = (dev_secrets_dict["FRONTEND_URL"][PYTHON_ENV],)
else:
    CORS_ORIGIN_ALLOW_ALL = True

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

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://learney-prod-redis.suk8h1.ng.0001.usw2.cache.amazonaws.com:6379",
        "TIMEOUT": 300,
    }
    if PYTHON_ENV != "dev"
    else {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
        "TIMEOUT": 300,
    }
}

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

CONN_MAX_AGE = None
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
    # https://docs.djangoproject.com/en/1.11/topics/security/
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 60
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    X_FRAME_OPTIONS = "DENY"

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
