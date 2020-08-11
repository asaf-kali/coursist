"""
Django settings for Coursist project.

Generated by 'django-admin startproject' using Django 3.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
from logging import NOTSET, WARNING, CRITICAL, INFO
from sys import stdout, stderr

import requests
from boto3 import Session

from academic_helper.utils.environment import is_prod, Environment, ENV
from academic_helper.utils.sentry import init_sentry

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "coursist.xyz"]

AWS_REGION = os.getenv("AWS_REGION", "eu-central-1")

if is_prod():
    try:
        internal_ip = requests.get("http://instance-data/latest/meta-data/local-ipv4").text
    except requests.exceptions.ConnectionError:
        pass
    else:
        ALLOWED_HOSTS.append(internal_ip)
    del requests

DEBUG = not is_prod()

SECRET_KEY = os.getenv("SECRET_KEY", "6*cne7$@#zo,;gl7#$%^*HSfda,msp2-034u5jt'vf=jvhj")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition
INSTALLED_APPS = [
    # Comments
    "django_comments",
    "course_comments",
    # Rating
    "star_ratings",
    # Cron
    "django_cron",
    # Db backup
    "dbbackup",
    # Our app
    "academic_helper",
    # Health check
    "health_check",
    # Storage
    "django_s3_storage",
    # Django base
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Login
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # "allauth.socialaccount.providers.facebook",  # Facebook login
    "allauth.socialaccount.providers.google",
]

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {"SCOPE": ["profile", "email",], "AUTH_PARAMS": {"access_type": "online",}},
    "facebook": {
        "METHOD": "oauth2",
        # 'SDK_URL': '//connect.facebook.net/{locale}/sdk.js',
        "SCOPE": ["email", "public_profile"],
        "AUTH_PARAMS": {"auth_type": "reauthenticate"},
        "INIT_PARAMS": {"cookie": True},
        "FIELDS": [
            "id",
            "email",
            "name",
            "first_name",
            "last_name",
            "verified",
            "locale",
            "timezone",
            "link",
            "gender",
            "updated_time",
        ],
        "EXCHANGE_TOKEN": True,
        "LOCALE_FUNC": lambda request: "en_US",
        "VERIFIED_EMAIL": False,
        "VERSION": "v7.0",
    },
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if ENV != Environment.prod:
    MIDDLEWARE += ["qinspect.middleware.QueryInspectMiddleware"]

ROOT_URLCONF = "Coursist.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates", "account"),
            os.path.join(BASE_DIR, "templates", "socialaccount"),
        ],
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

WSGI_APPLICATION = "Coursist.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DB_NAME", os.path.join(BASE_DIR, "db.sqlite3")),
    }
}

if ENV != Environment.local:
    DATABASES["default"]["USER"] = os.getenv("DB_USER", "admin")
    DATABASES["default"]["PASSWORD"] = os.getenv("DB_PASSWORD", "")
    DATABASES["default"]["HOST"] = os.getenv("DB_HOST", "")
    DATABASES["default"]["PORT"] = os.getenv("DB_PORT", "3306")

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# Logging

LOGGING_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGGING_DIR, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "aws": {"format": "[%(levelname)-.4s]: %(message)s @@@ [%(filename)s:%(lineno)s]"},
        "simple": {"format": "[%(asctime)s] [%(levelname)-.4s]: %(message)s", "datefmt": "%Y-%m-%d %H:%M:%S"},
        "verbose": {"format": "[%(asctime)s] [%(levelname)-.4s]: %(message)s @@@ [%(filename)s:%(lineno)s]"},
        "debug": {
            "format": "[%(asctime)s] [%(name)s] [%(levelname)-.4s]: %(message)s @@@ "
            "[%(threadName)s] [%(pathname)s:%(lineno)s]"
        },
    },
    "filters": {
        "std_filter": {"()": "academic_helper.utils.logger.LevelFilter", "low": INFO, "high": WARNING},
        "err_filter": {"()": "academic_helper.utils.logger.LevelFilter", "low": WARNING},
    },
    "handlers": {
        "console_out": {
            "class": "logging.StreamHandler",
            "filters": ["std_filter"],
            "formatter": "simple",
            "stream": stdout,
        },
        "console_err": {
            "class": "logging.StreamHandler",
            "filters": ["err_filter"],
            "formatter": "simple",
            "stream": stderr,
        },
        "root_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "root.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "level": "INFO",
            "when": "midnight",
            "backupCount": 14,
        },
        "coursist_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "coursist.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "when": "midnight",
        },
        "django_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "django.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "level": "INFO",
            "when": "midnight",
            "backupCount": 14,
        },
        "django_template_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "django_template.log"),
            "encoding": "utf-8",
            "formatter": "verbose",
            "level": "DEBUG",
            "when": "midnight",
            "backupCount": 7,
        },
        "debug_file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": os.path.join(LOGGING_DIR, "debug.log"),
            "encoding": "utf-8",
            "formatter": "debug",
            "when": "midnight",
            "backupCount": 7,
        },
    },
    "root": {"handlers": ["console_out", "console_err", "root_file"], "level": "INFO"},
    "loggers": {
        "coursist": {"handlers": ["coursist_file", "console_out", "console_err"], "level": "DEBUG", "propagate": False},
        "django": {"handlers": ["console_err", "django_file", "debug_file"], "level": "DEBUG", "propagate": False,},
        "django.utils.autoreload": {"level": "INFO", "propagate": True},
        "qinspect": {"handlers": ["debug_file", "console_out"], "level": "DEBUG", "propagate": False},
        "django.template": {"handler": ["django_template_file"], "level": "DEBUG", "propagate": False},
        "dbbackup": {"handlers": ["debug_file", "console_out"], "propagate": False},
        "py.warnings": {"handlers": ["debug_file"], "propagate": True},
    },
}

if ENV != Environment.local:
    session = Session(region_name=AWS_REGION)
    LOGGING["handlers"].update(
        {
            "cloudwatch-root": {
                "level": "INFO",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": session,
                "log_group": f"coursist-{ENV.name}",
                "stream_name": "root",
                "formatter": "aws",
            },
            "cloudwatch-coursist": {
                "level": "DEBUG",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": session,
                "log_group": f"coursist-{ENV.name}",
                "stream_name": "coursist",
                "formatter": "aws",
            },
            "cloudwatch-django": {
                "level": "INFO",
                "class": "watchtower.CloudWatchLogHandler",
                "boto3_session": session,
                "log_group": f"coursist-{ENV.name}",
                "stream_name": "django",
                "formatter": "aws",
            },
        }
    )
    LOGGING["root"]["handlers"].append("cloudwatch-root")
    LOGGING["loggers"]["coursist"]["handlers"].append("cloudwatch-coursist")
    LOGGING["loggers"]["django"]["handlers"].append("cloudwatch-django")

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

AUTH_USER_MODEL = "academic_helper.CoursistUser"

LANGUAGE_CODE = "en-US"

TIME_ZONE = "Asia/Jerusalem"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

if ENV == Environment.prod:
    # AWS settings
    DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"
    AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME", "coursist")
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_S3_BUCKET_NAME}.s3.amazonaws.com"
    # Static settings
    STATICFILES_STORAGE = "django_s3_storage.storage.StaticS3Storage"
    AWS_S3_BUCKET_NAME_STATIC = AWS_S3_BUCKET_NAME
    AWS_S3_KEY_PREFIX_STATIC = "static"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_S3_KEY_PREFIX_STATIC}/"
else:
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"
    STATIC_ROOT = os.path.join(BASE_DIR, "files/static")
    MEDIA_ROOT = os.path.join(BASE_DIR, "files/media")

# Auth
SITE_ID = 1
LOGIN_REDIRECT_URL = "/"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "optional"  # TODO change to mandatory
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # may sign in with either email or username
ACCOUNT_FORMS = {
    "login": "academic_helper.forms.CustomLoginForm.CustomLoginForm",
    "signup": "academic_helper.forms.CustomSignupForm.CustomSignupForm",
    "reset_password": "academic_helper.forms.CustomPasswordResetForm.CustomPasswordResetForm",
}
# Social auth
# SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIAL_AUTH_ACTIVATION = ENV == Environment.prod
SOCIALACCOUNT_EMAIL_REQUIRED = True
SOCIALACCOUNT_ADAPTER = "academic_helper.login_adapter.MySocialAccountAdapter"

# DB Backup
DBBACKUP_FILENAME_TEMPLATE = str(ENV.name) + "-{databasename}-{servername}-{datetime}.dump"
DBBACKUP_STORAGE = "django.core.files.storage.FileSystemStorage"
DBBACKUP_STORAGE_OPTIONS = {"location": "./backups"}

# Star rating
STAR_RATINGS_STAR_HEIGHT = 24
STAR_RATINGS_RANGE = 5  # needed for rating_for_comment
STAR_SIZE_FOR_COMMENT = 14

# Comments
COMMENTS_APP = "course_comments"

# Cron
CRON_CLASSES = [
    "academic_helper.logic.crons.BackupCron",
]

# Query inspect
QUERY_INSPECT_ENABLED = DEBUG
