from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid
from django.utils import timezone
# Create your models here.


def post_directory_path(instance, filename):
    extention = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{extention}'
    return f'posts/{instance.user.id}/{filename}'

class Posts(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=post_directory_path, null=True, blank=True)
    video = models.FileField(upload_to=post_directory_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField()
    likeCount = models.IntegerField(default=0)
    report_count = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user} - {self.content[:20]}'
    
    class Meta:
        ordering = ['-update_at']

    def save(self, *args, **kwargs):
        if not self.id:
            self.update_at = timezone.now()
        else:
            old_instance = Posts.objects.get(id=self.id)
            if old_instance.content != self.content or old_instance.image != self.image or old_instance.video != self.video:
                self.update_at = timezone.now()
        super().save(*args, **kwargs)
    
    
    


class FollowList(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)

    def __str__(self):
        return self.following.username
    

class PostLike(models.Model):
    post = models.ForeignKey(Posts,on_delete=models.CASCADE, related_name='liked_post')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='comment_post')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    likeCount = models.IntegerField(default=0)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='replies')

    class Meta:
        ordering = ['timestamp']

class CommentLike(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='liked_comment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)




class Notification(models.Model):


    notification_choices = [
        ("Like", "Like"),
        ("Comment", "Comment"),
        ("Follow", "Follow"),
        ("Reply", "Reply"),
    ]


    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='send_notifications')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, related_name='post_notifications', blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='comment_notifications', blank=True, null=True)
    action = models.CharField(max_length=20, choices=notification_choices)
    noti_content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} --> {self.recipient} : {self.action}'
    
    @classmethod
    def mark_as_seen(cls, user):
        cls.objects.filter(recipient=user, is_seen=False).update(is_seen=True)
    


class OpenedNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    noti_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.user.username
    


    
    


