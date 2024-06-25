import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()



from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from posts.routing import websocket_urlpatterns
from base.routing import websocket_urlpatterns as chat_webskt_patterns
from channels.auth import AuthMiddlewareStack
# from base.routing import websocket_urlpatterns



django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
                    AuthMiddlewareStack(
                            URLRouter(
                                websocket_urlpatterns+chat_webskt_patterns
                            )
                    )
                ),
})
# import os
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application
# from channels.security.websocket import AllowedHostsOriginValidator
# from posts.routing import websocket_urlpatterns
# from base.routing import websocket_urlpatterns as chat_webskt_patterns
# from channels.auth import AuthMiddlewareStack
# # from base.routing import websocket_urlpatterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# django_asgi_app = get_asgi_application()

# application = ProtocolTypeRouter({
#     "http": django_asgi_app,
#     "websocket": AllowedHostsOriginValidator(
#                     AuthMiddlewareStack(
#                             URLRouter(
#                                 websocket_urlpatterns+chat_webskt_patterns
#                             )
#                     )
#                 ),
# })

