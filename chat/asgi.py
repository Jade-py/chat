import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from base.routing import websocket_urlpatterns
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat.settings')

# Wrap Django's ASGI application with static files handler
django_asgi_app = get_asgi_application() # ASGI entry point defined for daphne in settings.py

application = ProtocolTypeRouter({
    "http": ASGIStaticFilesHandler(django_asgi_app), # if client sends HTTP request, wrapper serves static files
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns # if client sends websocket connection request
        )
    ),
})
