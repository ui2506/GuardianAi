from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('chat/', chat, name='chat'),
    path('message_test/', message_test),
    path('admin/', admin, name='admin'),
    path('admin/user_list/', user_list, name='user_list'),
    path('admin/calls/', admin_calls, name='calls'),
    path('admin/create_user/', create_user, name='create_user'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('register/', register, name='register'),

    path('admin_basement/', rickroll, name='troll')
]