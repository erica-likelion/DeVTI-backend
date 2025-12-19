# fmt: off
import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from config.routing import websocket_urlpatterns
from users.auth.ws_authentication import TokenAuthMiddleware
# fmt: on

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})
