import json
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Message,ChatRoom,User, UserOnlineStatus
from .serializers import ChatroomSerializer
from django.db.models import F, Q


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.chat_group_name = f'chat_{self.user_id}'
        
        async_to_sync(self.channel_layer.group_add)(
            self.chat_group_name, self.channel_name
        )
        self.accept()
        
        self.update_user_online(self.user_id)
        self.update_user_status(self.user_id)
        

    def receive(self,text_data):
        print('text data : ', text_data)
        text_data_json = json.loads(text_data)
        type_data = text_data_json['type']
        print('type : ', type)

        if type_data == 'chat':
            message = text_data_json['message']
            room_id = text_data_json['chatroomId']
            receiver_id = text_data_json['receiverId']
            
            Message.objects.create(room_id=room_id, sender_id=self.user_id, message=message)
            # if there is no room
            async_to_sync(self.channel_layer.group_send)(
                f'chat_{receiver_id}',{"type": "chat.message", "message":"new message"}
            )

            # to check 
            async_to_sync(self.channel_layer.group_send)(
                self.chat_group_name, {"type": "chat.message", "message":"new message"}
            )

            # self.chat_room_name = f'chat_room_{room_id}'

            # async_to_sync(self.channel_layer.group_add)(
            #     self.chat_room_name, self.channel_name
            # )

            # async_to_sync(self.channel_layer.group_send)(
            #     self.chat_room_name, {"type": "chat.message", "message":message}
            # )
        
        

    def disconnect(self, close_code):
        self.update_user_offline(self.user_id)
        
        self.update_user_status(self.user_id)

        # async_to_sync(self.channel_layer.group_discard)(
        #     self.chat_room_name, self.channel_name
        # )
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_group_name, self.channel_name
        )
        

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({"message":message}))

    def update_user_online(self,user_id):
        UserOnlineStatus.objects.filter(user_id=user_id).update(connections=F('connections')+1)
        UserOnlineStatus.objects.filter(user_id=user_id).first().update_status()

    def update_user_offline(self, user_id):
        UserOnlineStatus.objects.filter(user_id=user_id).update(connections=F('connections')-1)
        UserOnlineStatus.objects.filter(user_id=user_id).first().update_status()

    def user_status(self, event):
        room_id = event['room_id']
        room = get_object_or_404(ChatRoom, id=room_id)
        serializer = ChatroomSerializer(room)
        self.send(text_data=json.dumps({'chatroom':serializer.data}))

    def update_user_status(self, user_id):
        chat_list = ChatRoom.objects.filter(Q(user1_id=user_id) | Q(user2_id=user_id))
        for chat in chat_list:
            if chat.user1.id != user_id:
                async_to_sync(self.channel_layer.group_send)(
                    f'chat_{chat.user1.id}',{"type": "chat.message", "message":"user_status_changed"}
                )
            else:
                async_to_sync(self.channel_layer.group_send)(
                    f'chat_{chat.user2.id}',{"type": "chat.message", "message":"user_status_changed"}
                )



















#---------------------------------------------


# class ChatConsumer(WebsocketConsumer):

#     def connect(self):
#         self.user_id = self.scope['url_route']['kwargs']['user_id']
#         self.room_id = self.scope['url_route']['kwargs']['room_id']
#         self.room_group_name = f'chat_{self.room_id}'
        
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name, self.channel_name
#         )
        
#         self.accept()
#         self.update_user_online(self.user_id)

#         async_to_sync(self.channel_layer.group_send) (
#             self.room_group_name, {"type": "user_status", "room_id": self.room_id}
#         )
    

#     def receive(self,text_data):
        
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         Message.objects.create(room_id=self.room_id, sender_id=self.user_id, message=message)

#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name, {"type": "chat.message", "message":message}
#         )
        

#     def disconnect(self, close_code):
#         self.update_user_offline(self.user_id)
#         async_to_sync(self.channel_layer.group_send) (
#             self.room_group_name, {"type": "user_status", "room_id": self.room_id}
#         )

#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name, self.channel_name
#         )
        

#     def chat_message(self, event):
#         message = event['message']

#         self.send(text_data=json.dumps({"message":message}))

#     def update_user_online(self,user_id):
#         UserOnlineStatus.objects.filter(user_id=user_id).update(connections=F('connections')+1)
#         UserOnlineStatus.objects.filter(user_id=user_id).first().update_status()

#     def update_user_offline(self, user_id):
#         UserOnlineStatus.objects.filter(user_id=user_id).update(connections=F('connections')-1)
#         UserOnlineStatus.objects.filter(user_id=user_id).first().update_status()

#     def user_status(self, event):
#         room_id = event['room_id']
#         room = get_object_or_404(ChatRoom, id=room_id)
#         serializer = ChatroomSerializer(room)
#         self.send(text_data=json.dumps({'chatroom':serializer.data}))
    
        
        
