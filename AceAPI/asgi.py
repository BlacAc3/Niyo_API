"""
ASGI config for AceAPI project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from api.consumers import TaskConsumer
# from api.jwt_auth import JWTAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AceAPI.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/tasks/", TaskConsumer.as_asgi()),
        ])
    ),
    
})
