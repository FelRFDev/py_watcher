# myapp/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/system-monitor/$', consumers.SystemMonitorConsumer.as_asgi()),
    re_path(r'ws/docker-monitor/$', consumers.DockerMonitorConsumer.as_asgi()),
]