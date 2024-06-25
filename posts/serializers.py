from rest_framework import serializers
from .models import Posts,Comment, FollowList,Notification, CommentLike
from base.serializers import UserSerializer
from .utils import format_time




class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post_time = serializers.SerializerMethodField(read_only=True)
    comment_count = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Posts
        fields = ['id', 'user', 'content', 'image', 'likeCount', 'post_time', 'comment_count', 'video','report_count']

    def get_post_time(self, obj):
        return format_time(obj.update_at)
    
    def get_comment_count(self, obj):
        comment_count = obj.comment_post.all().count()
        return comment_count
    
    def validate(self, data):
        content = data.get('content')
        image = data.get('image')
        video = data.get('video')
        print(f'content : {content} image : {image} video : {video}')
        if not content and not image and not video:
            raise serializers.ValidationError("Post can't be null")
        return data
        


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    isUserLiked = serializers.SerializerMethodField(read_only=True)
    count_replies = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Comment
        fields = ['id', 'user', 'post', 'content', 'time', 'likeCount', 'parent','isUserLiked','count_replies']

    def get_isUserLiked(self, obj):
        user_id = self.context.get('user_id')
        ob = CommentLike.objects.filter(user__id=user_id,comment=obj)
        if ob:
            return True
        return False
    
    def get_count_replies(self, obj):
        replies = Comment.objects.filter(parent=obj)
        if replies:
            return replies.count()
        return 0
    
    def get_time(self, obj):
        return format_time(obj.timestamp)


class FollowListSerializer(serializers.ModelSerializer):
    following = UserSerializer(read_only=True)
    follower = UserSerializer(read_only=True)
    class Meta:
        model = FollowList
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'