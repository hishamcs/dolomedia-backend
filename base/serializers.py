from .models import User, ChatRoom, Message, UserOnlineStatus
from posts.models import FollowList
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from drf_extra_fields.fields import Base64ImageField 
import base64
from posts.utils import format_time
from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator,MinLengthValidator, MaxLengthValidator
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)
    is_online = serializers.SerializerMethodField(read_only=True)
    is_following = serializers.SerializerMethodField(read_only=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^(?=.*[0-9])(?=.*[a-zA-Z])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,20}$',
                message='Password should be 8-20 characters and include at least 1 letter, 1 number, and 1 special character'
            )
        ]
    )
    first_name = serializers.CharField(
        required=True,
        validators=[
            MinLengthValidator(3, message='User name should be at least 3 characters.'),
            MaxLengthValidator(16, message='User name should be at most 16 characters.'),
            RegexValidator(
                regex=r'^[a-zA-Z]+$',
                message='User name should only contain alphanumeric characters'
            )
        ]
    )

    phone = serializers.CharField(
        required=True,
        write_only=True,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message='Please Enter a valid Mobile Number'
            )
        ]
    )
    
    class Meta:
        model = User
        fields = ['id','email', 'name','is_active','isAdmin','pro_pic', 'cover_pic', 'is_online', 'password', 'first_name', 'phone', 'is_following']

    
    def get_name(self, obj):
        name = obj.first_name
        if name == '':
            name = obj.email
        return name
    
    def get_isAdmin(self, obj):
        return obj.is_staff
    
    def get_is_online(self, obj):
        status = get_object_or_404(UserOnlineStatus, user=obj)
        return status.is_online
    
    def get_is_following(self, obj):
        request = self.context.get('request', None)
        if request is None or request.user.is_anonymous:
            return False
        current_user = request.user
        return FollowList.objects.filter(following=obj, follower=current_user).exists()
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise ValidationError('The email already used')
        return value
    
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise ValidationError('The Phone already used')
        return value
    
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
    

# class UserSerializerWithToken(UserSerializer):
#     token = serializers.SerializerMethodField(read_only=True)
#     class Meta:
#         model = User
#         fields = ['id','email', 'name','token','isAdmin', 'pro_pic', 'cover_pic']

#     def get_token(self, obj):
#         token = RefreshToken.for_user(obj)
#         return str(token.access_token)

class UserPictureSerailzer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['pro_pic', 'cover_pic']


class ChatroomSerializer(serializers.ModelSerializer):
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    last_message = serializers.SerializerMethodField(read_only=True)
    last_msg_read = serializers.SerializerMethodField(read_only=True)
    sender_id = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = ChatRoom
        fields = ['id', 'user1', 'user2', 'last_message', 'last_msg_read', 'sender_id']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-id').first()
        if last_message:
            return last_message.message if len(last_message.message)<15 else last_message.message[:15]
        return None
        
    def get_last_msg_read(self, obj):
        last_message = obj.messages.order_by('-id').first()
        if last_message and last_message.is_read:
            return True
        return False
    def get_sender_id(self, obj):
        last_msg = obj.messages.last()
        if last_msg:
            return last_msg.sender.id
        return None
        
    


class MessageSerializer(serializers.ModelSerializer):
    timestamp =serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Message
        fields = '__all__'

    def get_timestamp(self, obj):
        return format_time(obj.timestamp)

    