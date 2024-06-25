import json 

from channels.generic.websocket import WebsocketConsumer
from .models import Notification,OpenedNotification


from asgiref.sync import async_to_sync
import json

class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        print('working')
        self.room_name = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'notification_{self.room_name}'
        
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        #notifications = Notification.objects.filter(recipient_id=self.room_name, is_seen=False).count()
        notifications = OpenedNotification.objects.get(user_id=self.room_name).noti_count
        # print('notificaitons : ', notifications)
        self.accept()
        self.send(text_data=json.dumps({'message':notifications}))
    def receive(self, text_data):
        pass

    def disconnect(self, close_code):
        print('disconnect code : ', close_code)
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def send_notifications(self, event):
        message = event['message']
        
        self.send(text_data=json.dumps({'message':message}))
