from django.urls import path
from .views import *


urlpatterns = [
    path('fetch-posts/', PostsView.as_view()),
    path('addposts/', PostsView.as_view()),
    path('update-posts/', PostsView.as_view()),
    path('admin-posts/', PostsView.as_view()),
    path('usersuggestion/<int:user_id>',UserSuggestions.as_view()),
    path('follow-user/<int:fuser_id>/',FollowUser.as_view()),
    path('like-post/', PostLikes.as_view()),
    path('like-post/<int:user_id>/<int:post_id>', PostLikes.as_view()),
    path('comment/',CommentView.as_view(),name='comment'),
    path('profile/<int:user_id>',ProfileView.as_view()),
    path('profile/following-list/', FollowingList.as_view()),
    path('profile/follower-list/', FollowingList.as_view()),
    path('post-delete/', PostsView.as_view()),
    path('post-report/', PostsView.as_view()),
    path('notifications/', NotificationView.as_view()),
    path('like-comment/',CommentLikeView.as_view()),
]
