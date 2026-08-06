from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import ChatRoom, Message
from .forms import ChatRoomForm, MessageForm


@login_required
def chat_room_list(request):
    chat_rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, 'chat/chat_room_list.html', {
        'chat_rooms': chat_rooms
    })


@login_required
def chat_room_detail(request, pk):
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    if request.user not in chat_room.participants.all():
        messages.error(request, 'Access denied.')
        return redirect('chat:chat_room_list')
    
    messages_list = chat_room.messages.all()[:50]
    
    return render(request, 'chat/chat_room_detail.html', {
        'chat_room': chat_room,
        'messages': messages_list
    })


@login_required
def create_chat_room(request):
    if request.method == 'POST':
        form = ChatRoomForm(request.POST)
        if form.is_valid():
            chat_room = form.save(commit=False)
            chat_room.created_by = request.user
            chat_room.save()
            chat_room.participants.add(request.user)
            messages.success(request, 'Chat room created successfully.')
            return redirect('chat:chat_room_detail', pk=chat_room.pk)
    else:
        form = ChatRoomForm()
    
    return render(request, 'chat/chat_room_form.html', {
        'form': form
    })


@login_required
def send_message(request, pk):
    chat_room = get_object_or_404(ChatRoom, pk=pk)
    
    if request.user not in chat_room.participants.all():
        messages.error(request, 'Access denied.')
        return redirect('chat:chat_room_list')
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.room = chat_room
            message.sender = request.user
            message.save()
            messages.success(request, 'Message sent.')
    
    return redirect('chat:chat_room_detail', pk=chat_room.pk)
