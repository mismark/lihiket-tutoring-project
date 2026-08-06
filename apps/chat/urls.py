from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_room_list, name='chat_room_list'),
    path('<int:pk>/', views.chat_room_detail, name='chat_room_detail'),
    path('create/', views.create_chat_room, name='create_chat_room'),
    path('<int:pk>/send/', views.send_message, name='send_message'),
]