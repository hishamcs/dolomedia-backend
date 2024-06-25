from django.contrib import admin
from .models import *
# Register your models here.

class PostAdmin(admin.ModelAdmin):
    list_display=('id','user', 'content', 'image', 'created_at', 'update_at','likeCount', 'report_count')

admin.site.register(Posts,PostAdmin)
admin.site.register(Comment)
admin.site.register(FollowList)
admin.site.register(PostLike)
admin.site.register(Notification)
admin.site.register(OpenedNotification)
