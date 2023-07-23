from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/socket-server/player', consumers.GameConsumer.as_asgi()),
    re_path(r'ws/socket-server/admin', consumers.AdminConsumer.as_asgi())
]