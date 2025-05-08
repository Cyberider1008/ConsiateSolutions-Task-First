from django.urls import re_path
from app1.consumers import OrderConsumer

websocket_urlpatterns = [
    re_path(r'^ws/orders/', OrderConsumer.as_asgi()), # ws://localhost:8000/ws/orders/ 
]