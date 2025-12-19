from .base import *
import os

DEBUG = False

# ALLOWED_HOSTS
hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if hosts:
    ALLOWED_HOSTS = [h.strip() for h in hosts.split(",")]
else:
    ALLOWED_HOSTS = []

# HTTPS
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CORS
CORS_ALLOW_CREDENTIALS = True
cors_origins_prod = os.getenv("CORS_ALLOWED_ORIGINS_PROD", "")
if cors_origins_prod:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in cors_origins_prod.split(",")]
else:
    CORS_ALLOWED_ORIGINS = []

# CSRF
csrf_origins_prod = os.getenv("CSRF_TRUSTED_ORIGINS_PROD", "")
if csrf_origins_prod:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in csrf_origins_prod.split(",")]
else:
    CSRF_TRUSTED_ORIGINS = []

# COOKIE
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
