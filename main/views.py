from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse

from .models import Call, ChatMessage

User = auth.get_user_model()

def home (request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html', {'user': request.user})

def message_test (request: HttpRequest) -> HttpResponse:
    messages.info(request, 'info message test')
    messages.success(request, 'success message test')
    messages.error(request, 'error message test')
    messages.warning(request, 'warning message test')

    return redirect('home')

def chat (request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        messages.error('Хей хей, куда спешим? С начало надо войти в аккаунт.')
        return redirect('home')

    return render(request, 'chat.html')

def admin (request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        # messages.warning(request, 'Ай ай ай, куда лезим? У вас нет админ прав XD')
        return redirect('troll')
    
    return render(request, 'admin/main.html')

def user_list(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        # messages.warning(request, 'Ай ай ай, куда лезим? У вас нет админ прав XD')
        return redirect('troll')
    
    if request.method == 'POST':
        user_id = request.POST.get('clear_history')

        if user_id:
            target = User.objects.get(id=user_id)

            if not target:
                messages.error(request, 'Пользователь не найден...')
                return redirect('user_list')

            ChatMessage.objects.filter(user=target).delete()
            Call.objects.filter(target=target).delete()
            messages.success(request, 'История успешно очищена!')
    
    users = User.objects.all().order_by('-date_joined')

    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/user_list.html', {'page_obj': page_obj})

def admin_calls (request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        # messages.warning(request, 'Ай ай ай, куда лезим? У вас нет админ прав XD')
        return redirect('troll')
    
    if request.method == 'POST':
        take_id = request.POST.get('take')
        delete_id = request.POST.get('delete')

        if take_id:
            call = Call.objects.get(id=take_id)

            if not call:
                messages.error(request, 'Не удалось найти обьект!')
                return redirect('calls')
            
            if call.is_taken:
                messages.warning(request, 'Уже находится на рассмотрений.')
                return redirect('calls')
            
            call.is_taken = True
            call.save()

            messages.success(request, 'Вы успешно взяли обращение!')
            return redirect('calls')
        
        if delete_id:
            call = Call.objects.get(id=delete_id)

            if not call:
                messages.error(request, 'Не удалось найти обьект!')
                return redirect('calls')
            
            if not call.is_taken:
                messages.warning(request, 'Нельзя удалить обращение без рассмотрение.')
                return redirect('calls')
            
            call.delete()

            messages.success(request, 'Обращение успешно удалено.')
            return redirect('calls')
    
    calls = Call.objects.all()

    return render(request, 'admin/calls.html', {'calls': calls})

def create_user(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        return redirect('troll')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Имя пользователя и пароль обязательны!')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Такой пользователь уже существует!')
        else:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                password=password
            )
            messages.success(request, f'Пользователь {user.username} успешно создан!')
            return redirect('user_list')

    return render(request, 'admin/create_user.html')

def register (request: HttpRequest) -> HttpResponse:
    user = request.user

    if user.is_authenticated:
        messages.warning(request, 'Вы уже зарегестрированы!')
        return redirect(home)
    
    messages.warning(request, 'Пожалуйста, пройдите регистрацию через администратора!')
    return redirect(home)

def logout (request: HttpRequest) -> HttpResponse:
    if not request.user.is_authenticated:
        messages.warning(request, 'Эй эй эй, куда такая спешка? Ты даже не вошел в аккаунт.')
        return redirect(home)
    
    auth.logout(request)
    messages.success(request, 'Вы вышли с аккаунта :(')
    return redirect('home')

def login (request: HttpRequest) -> HttpResponse:
    user = request.user

    if user.is_authenticated:
        messages.warning(request, 'Вы уже вошли в аккаунт. Зачем снова пытатся зайти? :/')
        return redirect(home)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.warning(request, 'Ммм мне кажется все поля должны быть заполнены')
            return redirect('login')
        
        new_user = auth.authenticate(request, username=username, password=password)

        if not new_user:
            messages.warning(request, 'Я не вижу пользователя с таким паролем и никнеймом')
            return redirect('login')

        auth.login(request, new_user)

        messages.success(request, 'Вы успешно вошли в аккаунт!')
        return redirect('home')
    
    return render(request, 'auth/login.html')

def rickroll (request: HttpRequest) -> HttpResponse:
    return render(request, 'rickroll.html')