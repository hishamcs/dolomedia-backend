from django.apps import AppConfig

from django.db.models.signals import post_save

class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self):
        from . import signals
