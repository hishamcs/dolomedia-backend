from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
# Create your models here.


def user_directory_path(instance, filename):
    extention = filename.split('.')[-1]
    filename = f'{uuid.uuid4().hex}.{extention}'
    return f'users/user_{instance.id}/{filename}'
class User(AbstractUser):
    phone = models.CharField(max_length=10, unique=True, null=True)
    pro_pic = models.ImageField(
        upload_to=user_directory_path,
        blank=True, null=True, default='images/pro_pic.png'
    )
    cover_pic = models.ImageField(
        upload_to=user_directory_path,
        blank=True, null=True, default='images/cover_pic.png')

class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user1',null=True)
    user2 = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='user2', null=True)

    class Meta:
        ordering = ['-id']
    
    def __str__(self):
        return f'{self.user1.username}<---->{self.user2.username}'
    
    

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='send_msgs', null=True)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.sender.username
    class Meta:
        ordering = ['timestamp']    

class UserOnlineStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    is_online = models.BooleanField(null=True, blank=True, default=False)
    connections = models.PositiveIntegerField(null=True, blank=True,default=0)



    def __str__(self):
        return f'{self.user.username}--{self.connections} --{self.is_online}'

    def update_status(self):
        if self.connections>0:
            self.is_online =True
        else:
            self.is_online = False
        self.save()


    
    
