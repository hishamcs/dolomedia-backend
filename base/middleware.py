from rest_framework_simplejwt.tokens import AccessToken
from .models import User
from django.contrib.auth.hashers import check_password
import json
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer

def block_wrapper(func):
    def check_user_block(request):
        token = request.META.get('HTTP_AUTHORIZATION')
        # print(f'From middleware \n path:{request.path} and token:{token}')
        if token is None and request.path == '/api/user/login/':
            raw_data = request.body
            # print('raw data :', raw_data)
            json_data = json.loads(raw_data.decode('utf-8'))

            username = json_data['username']
            password = json_data['password']
            
            user = User.objects.get(username=username)
            if check_password(password,user.password):
                    if user.is_active == False:
                        message = {'detail':'You are blocked by admin...'}
                        response = Response(message, status=status.HTTP_403_FORBIDDEN)
                        response.accepted_renderer = JSONRenderer()
                        response.accepted_media_type = 'application/json'
                        response.renderer_context = {}
                        response.render()
                        return response
        return func(request)
    return check_user_block




