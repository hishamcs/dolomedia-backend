from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import APIView
from base.models import User
from .serializers import PostSerializer,CommentSerializer,FollowListSerializer, NotificationSerializer
from base.serializers import UserSerializer
from .models import FollowList,Posts,PostLike,Comment,Notification, OpenedNotification, CommentLike
from django.db.models import F
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from rest_framework import status
from rest_framework.settings import api_settings
import os
from rest_framework.pagination import PageNumberPagination
import boto3
from django.db import transaction


# Create your views here.

class PostsView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
    def post(self, request):
        user_id = request.data.get('userId')
        if not user_id:
            return Response({'error : userId is required...'}, status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(User, id=user_id)
        serializer = self.serializer_class(data=request.data)
        content = request.data.get('content')
        image = request.data.get('image')
        video = request.data.get('video')
        print('content : ', request.data)
        if serializer.is_valid():
            serializer.save(user=user, image=image, content=content, video=video)
            return Response({'message':'success'}, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # def get(self, request):
    #     user_id = request.GET.get('userId')
    #     if user_id is None:
    #         return Response({'error':'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
    #     try:
    #         user = get_object_or_404(User, id=user_id)
    #         user_following = list(user.following.all().values_list('following_id',flat=True))
    #         user_following.append(user.id)
    #         posts = Posts.objects.filter(user__in=user_following)
    #         serializer = self.serializer_class(posts, many=True)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         print('exception  :', e)
    #         return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)


    def get(self, request):
        user_id = request.user.id
        if user_id is None:
            return Response({'error':'User id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if request.user.is_superuser:
                posts = Posts.objects.all()
                serializer = self.serializer_class(posts, many=True)
                return Response(serializer.data,status=status.HTTP_200_OK)
            user = get_object_or_404(User, id=user_id)
            user_following = list(user.following.all().values_list('following_id',flat=True))
            user_following.append(user.id)
            posts = Posts.objects.filter(user__in=user_following)
            page = self.paginate_queryset(posts)
            if page is not None:
                serializer = self.serializer_class(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = self.serializer_class(posts, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print('exception  :', e)
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    def delete_s3_media_file(self, file_path):
        s3 = boto3.client('s3')
        try:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_path)
        except Exception as e:
            raise Exception(f'Failed to delete the media file : {str(e)}')
        

    def delete(self, request):
        post_id = request.GET.get('postId')
        try:
            post = Posts.objects.get(id=post_id)
            if post.image:
                try:
                    self.delete_s3_media_file(str(post.image))
                except Exception as e:
                    return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if post.video:
                try:
                    self.delete_s3_media_file(str(post.video))
                except Exception as e:
                    return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            post.delete()
            posts = Posts.objects.all()
            serializer = self.serializer_class(posts, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Posts.DoesNotExist:
            return Response({'error':'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    
    # def delete(self, request):
    #     post_id = request.GET.get('postId')
    #     try:
    #         post = Posts.objects.get(id=post_id)
    #         if post.image:
    #             image_file_path = os.path.join(settings.MEDIA_ROOT, str(post.image))
    #             if os.path.exists(image_file_path):
    #                 os.remove(image_file_path)
    #             else:
    #                 return Response({'error':'Image file doesnot exist'}, status=status.HTTP_404_NOT_FOUND)
            
    #         if post.video:
    #             video_file_path = os.path.join(settings.MEDIA_ROOT, str(post.video))
    #             if os.path.exists(video_file_path):
    #                 os.remove(video_file_path)
    #             else:
    #                 return Response({'error':'Video file doesnot exist'},status=status.HTTP_404_NOT_FOUND)
    #         post.delete()
    #         posts = Posts.objects.all()
    #         serializer = self.serializer_class(posts, many=True)
    #         return Response(serializer.data,status=status.HTTP_200_OK)
    #     except Posts.DoesNotExist:
    #         return Response({'error':'Post not found'}, status=status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    
    def patch(self, request):
        print('daat : ', request.data)
        post_id = request.data.get('postId')
        info = request.data.get('info')
        if post_id is None:
            return Response({'error':'postid is required'}, status=status.HTTP_400_BAD_REQUEST)
        post = get_object_or_404(Posts, id=post_id)
        if info == 'Report':
            post.report_count += 1
            post.save()
            return Response({'message':'Reported'}, status=status.HTTP_200_OK) 
        serializer = self.serializer_class(instance=post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message':'success'}, status=status.HTTP_200_OK)
        else:
            print('errors : ', serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # post_id = request.data.get('postId')
        # post = Posts.objects.get(id=post_id)
        # post.report_count += 1
        # post.save()


    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator
    

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        # print(queryset)
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)
    

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)



class UserSuggestions(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request,user_id):
        user = User.objects.get(id=user_id)
        users = User.objects.filter(is_superuser=False).exclude(id=user_id)
        users_followings = user.following.all()
        suggestions = users.exclude(followers__in=users_followings)
        serializer = UserSerializer(suggestions, many=True)
        return Response(serializer.data)


class FollowUser(APIView):
    def post(self, request, fuser_id):
        print('request .data : ', request.data)
        info = request.data.get('info')
        search_content = request.data.get('search_content')


        user_id = request.user.id
        user = User.objects.get(id=user_id)
        follows = User.objects.get(id=fuser_id)


        with transaction.atomic():
            follow_relation, created = FollowList.objects.get_or_create(follower=user, following=follows)

            if not created:
                follow_relation.delete()
            else:
                status = f'{user.first_name} started to following you'
                Notification.objects.create(sender=user, recipient=follows, action="Follow", noti_content=status)
                OpenedNotification.objects.filter(user=follows).update(noti_count=F('noti_count')+1)  

        if search_content and info == 'SearchResult':
            users = User.objects.filter(first_name__icontains=search_content).exclude(id=user_id)
            searilizer = UserSerializer(users, many=True, context={'request':request})
            return Response(searilizer.data)
        elif info == 'Following List':
            following_list = user.following.all()
            serializer = FollowListSerializer(following_list, many=True, context={'request':request})
            return Response(serializer.data)
        elif info == 'Followers List':
            followers_list = user.followers.all()
            serializer = FollowListSerializer(followers_list, many=True, context={'request':request})
            return Response(serializer.data)
        elif info == 'suggestion':
            user_following = user.following.all()
            users = User.objects.filter(is_superuser=False).exclude(id=user_id)
            suggested_users = users.exclude(followers__in=user_following)
            serializer = UserSerializer(suggested_users, many=True)
            return Response(serializer.data)
        else:
            serializer = UserSerializer(follows, context={'request':request})
            return Response(serializer.data)




#info ==search, followerlist, following list
# class FollowUser(APIView):
#     def post(self, request, fuser_id):
#         print('request .data : ', request.data)
#         user_id = request.user.id
#         user = User.objects.get(id=user_id)
#         follows = User.objects.get(id=fuser_id)
#         FollowList.objects.create(follower=user, following=follows)
#         status = f'{user.username} started to following you'
#         Notification.objects.create(sender=user, recipient=follows, action="Follow", noti_content=status)
#         OpenedNotification.objects.filter(user=follows).update(noti_count=F('noti_count')+1)
#         user_following = user.following.all()
#         users = User.objects.filter(is_superuser=False).exclude(id=user_id)
#         suggested_users = users.exclude(followers__in=user_following)
#         serializer = UserSerializer(suggested_users, many=True)
#         return Response(serializer.data)
    

class PostLikes(APIView):
    def get(self,request,user_id,post_id):
        post = Posts.objects.get(id=post_id)
        user = User.objects.get(id=user_id)
        post_like = PostLike.objects.filter(user__id=user_id, post__id=post_id)
        if post_like:
            post_like.delete()
            post.likeCount -= 1
            response = {'postliked':False,'likeCount':post.likeCount}
            if user!=post.user:
                notification = Notification.objects.get(sender=user, recipient=post.user, post=post, action="Like")
                OpenedNotification.objects.filter(user=post.user, noti_count__gt=0).update(noti_count=F('noti_count')-1)
                notification.delete()
        else:
            PostLike.objects.create(user_id=user_id,post_id=post_id, liked=True)
            post.likeCount += 1
            response = {'postliked':True,'likeCount':post.likeCount}
            ##########
            if user!=post.user:
                status = f'{user.username} Likes your post'
                notification = Notification.objects.create(sender=user, recipient=post.user, post=post, action="Like", noti_content=status)
                OpenedNotification.objects.filter(user=post.user).update(noti_count=F('noti_count')+1)
        post.save()
        return Response(response)
    
    def post(self, request):
        user_id = request.data.get('user_id')
        post_id = request.data.get('post_id')
        post = Posts.objects.get(id=post_id)
        comment_count = post.comment_post.filter(parent=None).count()
        like_count = post.likeCount
        like_post = PostLike.objects.filter(user__id=user_id, post__id=post_id)
        if like_post:
            islike_post = like_post[0].liked
        else:
            islike_post = False
        response = {'isLikePost':islike_post,'likeCount':like_count,'commentCount':comment_count}
        return Response(response)
    

class CommentView(APIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    def post(self,request):
        comment_id = request.data.get('commentId')
        
        if comment_id:
            parent = get_object_or_404(Comment, id=comment_id)
            # user_id = request.data.get('userId')
            # user = get_object_or_404(User, id=user_id)
            user = request.user
            reply_id = request.data.get('replyId', None)
            reply = Comment.objects.filter(id=reply_id)
            post = parent.post
            content = request.data.get('content')
            serializer = self.serializer_class(data=request.data)
            print(f'user : {user} parent.user : {parent.user}')
            if serializer.is_valid():
                cmt = serializer.save(user=user, post=post, content=content, parent=parent)
                if user!=parent.user:
                    status = f'{user.username} is replied to your comment'
                    Notification.objects.create(sender=user, recipient=parent.user, post=post, comment=cmt, action="Reply", noti_content=status)
                    OpenedNotification.objects.filter(user=parent.user).update(noti_count=F('noti_count')+1)
                elif reply and reply[0].user!=user:
                    status = f'{user.username} is replied to your comment'
                    Notification.objects.create(sender=user, recipient=reply[0].user, post=post, comment=cmt, action="Reply", noti_content=status)
                    OpenedNotification.objects.filter(user=reply[0].user).update(noti_count=F('noti_count')+1)
                replies = Comment.objects.filter(parent=parent)
                serializer = self.serializer_class(replies, many=True)
                return Response(serializer.data)
            else:
                print(serializer.errors)
                return Response(serializer.errros)
            
            
        else:
            content = request.data.get('content')
            # user_id = request.data.get('userId')
            user_id = request.user.id
            post_id = request.data.get('postId')
            user = get_object_or_404(User, id=user_id) 
            post_instance = get_object_or_404(Posts, id=post_id)
            serializer = self.serializer_class(data=request.data)
            
            if serializer.is_valid():
                cmt = serializer.save(post=post_instance,content=content, user=user)
                if user_id != post_instance.user.id:
                    status = f'{user.username} commented on your post'
                    Notification.objects.create(sender=user, recipient=post_instance.user, post=post_instance, comment=cmt, action="Comment", noti_content=status)
                    OpenedNotification.objects.filter(user=post_instance.user).update(noti_count=F('noti_count')+1)
                comments = Comment.objects.filter(post__id=post_id, parent=None)
                serializer = self.serializer_class(comments, many=True)
                return Response(serializer.data)
            else:
                print(serializer.errors)
                return Response(serializer.errors)
            

    
    def get(self,request):
        comment_id = request.GET.get('commentId')
        post_id = request.GET.get('postId')
        # user_id = request.GET.get('userId')
        user_id = request.user.id
        if comment_id:
            comment = Comment.objects.get(id=comment_id)
            replies = comment.replies.all()
            # print('replies : ', replies)
            serializer = self.serializer_class(replies, many=True, context={'user_id':user_id})
            return Response(serializer.data)
        
        comments = Comment.objects.filter(post__id=post_id, parent=None)
        serializer = self.serializer_class(comments, many=True, context={'user_id':user_id})
        return Response(serializer.data)
    
    def delete(self, request):
        comment_id = request.GET.get('commentId')
        user_id = request.user.id
        if not comment_id:
            return Response({'error':'comment id is required...'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_id:
            return Response({'error':'user id is required...'}, status=status.HTTP_400_BAD_REQUEST)
        comment = get_object_or_404(Comment, id=comment_id)
        parent = comment.parent
        comment_post = comment.post
        comment.delete()
        if parent:
            print('parent of the comment : ', parent)
            replies = parent.replies.all()
            serializer = self.serializer_class(replies, many=True, context={'user_id':user_id})
        else:
            print('post of the comment : ', comment_post)
            comments = Comment.objects.filter(post=comment_post, parent=None)
            serializer = self.serializer_class(comments, many=True, context={'user_id':user_id})

        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        comment_id = request.data.get('commentId')
        if not comment_id:
            return Response({'error':'Comment id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            comment = get_object_or_404(Comment, id=comment_id)
        except Comment.DoesNotExist:
            return Response({'error':'Comment Doesnot exist'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(instance=comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            if comment.parent:
                comments = Comment.objects.filter(parent=comment.parent) # Replies
            else:
                comments = Comment.objects.filter(post=comment.post)
            serializer = self.serializer_class(comments, many=True)
            return Response({'message':'updated successfully', 'data':serializer.data}, status=status.HTTP_200_OK)
        else:
            print(serializer.errors)
            return Response({'error':serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    

class ProfileView(APIView):
    def get(self,request, user_id):
        
        user = User.objects.get(id=user_id)
        following = user.following.all().count()
        followers = user.followers.all().count()
        posts = Posts.objects.filter(user__id=user_id)
        post_serializer = PostSerializer(posts,many=True,context={'request':request})
        user_serializer = UserSerializer(user,context={'request':request})
        serializer_data = {
            'user':user_serializer.data,
            'posts':post_serializer.data,
            'followersCount':followers,
            'followingCount':following,
        }
        return Response(serializer_data) 

class FollowingList(APIView):
    
    serializer_class = FollowListSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request):
        info = request.data.get('info')
        user = request.user
        
        if info:
            followers_list = user.followers.all()
            serializer = self.serializer_class(followers_list, many=True, context={'request':request})
            return Response(serializer.data)
        
        following_list = user.following.all()
        serializer = self.serializer_class(following_list, many=True, context={'request':request})
        
        return Response(serializer.data)      



class NotificationView(APIView):
    serializer_class = NotificationSerializer

    def get(self,request):
        user_id = request.GET.get('userId')
        notifications = Notification.objects.filter(recipient_id=user_id, is_seen=False).order_by('-timestamp')
        OpenedNotification.objects.filter(user_id=user_id).update(noti_count=0)
        not_seen_notif_count = OpenedNotification.objects.get(user_id=user_id)
        not_seen_notif_count.noti_count = 0
        not_seen_notif_count.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notification_{user_id}', {'type':'send.notifications', 'message':not_seen_notif_count.noti_count}
        )
        serializer = self.serializer_class(notifications, many=True)
        return Response({'notifications':serializer.data})
    
    def post(self, request):
        Notification.mark_as_seen(request.user)
        return Response({'message':'success'}, status=status.HTTP_200_OK)
    


class CommentLikeView(APIView):
    def get(self, request):
        return Response({'message':'success'})
    def post(self, request):
        user_id = request.user.id
        comment_id = request.data.get('commentId')
        comment = Comment.objects.get(id=comment_id)
        comment_like = CommentLike.objects.filter(user__id=user_id, comment__id=comment_id)
        
        if comment_like:
            comment_like[0].delete()
            comment.likeCount -= 1
            if user_id != comment.user.id:
                notification = Notification.objects.get(sender__id=user_id,recipient=comment.user, comment=comment, action='Like')
                OpenedNotification.objects.filter(user=comment.user, noti_count__gt=0).update(noti_count=F('noti_count')-1)
                notification.delete()
            response = {'commentLike':False, 'likeCount':comment.likeCount}
        else:
            CommentLike.objects.create(user_id=user_id, comment_id=comment_id)
            comment.likeCount += 1
            if user_id != comment.user.id:
                user = User.objects.get(id=user_id)
                status = f'{user.username} Likes your comment'
                Notification.objects.create(sender=user, recipient=comment.user, comment=comment, action='Like', noti_content=status)
                OpenedNotification.objects.filter(user=comment.user).update(noti_count=F('noti_count')+1)
            response = {'commentLike':True, 'likeCount':comment.likeCount}
        comment.save()
            
        return Response(response)       
    








