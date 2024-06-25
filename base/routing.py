from django.urls import path
from .consumers import *

websocket_urlpatterns = [
    path("ws/chat/<int:user_id>/", ChatConsumer.as_asgi()),
    # path("ws/chat/<int:room_id>/<int:user_id>/", ChatConsumer.as_asgi()),
]