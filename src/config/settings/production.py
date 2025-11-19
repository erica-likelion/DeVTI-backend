from .base import *
import os

DEBUG = False
# ALLOWED_HOSTS를 .env에서 읽도록 설정
# env에서 허용할 도메인, IP 여러개 받아와서 리스트 형태로 저장 (없으면 공백으로 저장)
hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "")

if hosts:
    ALLOWED_HOSTS = [h.strip() for h in hosts.split(",")]
else:
    ALLOWED_HOSTS = []

# HTTPS 설정 등... (추후 추가)
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True
