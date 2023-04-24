from django.shortcuts import render, redirect
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.dispatch.dispatcher import receiver
from django.contrib.sessions.models import Session
from .models import UserSession
from django.views.generic.edit import CreateView

#from hcaptcha.fields import hCaptchaField

login_tries = {}
tries = 1

def logout(request):
    #Desloga o usuário
    auth.logout(request)
    return redirect('login')

def login(request):
    global login_tries
    global tries
    LOGIN_TRIES_MAX = 3
    
    #Se não estiver tentando logar, ele apenas abre a tela de login
    if  request.method != 'POST':
        return render(request, 'accounts/login.html')

    #Recebe o usuário e senha
    user = request.POST.get('user')
    password = request.POST.get('password')

    #Autentica se o usuário e a senha existem
    user_authenticated = auth.authenticate(request, username=user, password=password)

    try:
        #Verifica se existe o usuário
        db_user = User.objects.get(username=user)

        #Se o usuário não for autenticado, soma nas tentativas de login
        if not user_authenticated:
            for key in login_tries.keys():
                if key == user:
                    tries = login_tries[user] + 1
                    break
                if key == list(login_tries)[-1]:
                    tries = 1
            login_tries[user] = tries

            tries = login_tries[user] + 1

            #Se errou a senha mais ou igual o número máximo de tentativas, bloqueia o usuário
            if login_tries[user] >= LOGIN_TRIES_MAX:
                db_user.is_active = False
                login_tries[user] = 0
                db_user.save()

        if not db_user.is_active:
            messages.error(request, 'Usuário Bloqueado')
            return render(request, 'accounts/login.html')
    except:
        messages.error(request, 'Usuário ou senha inválidos')
        return render(request, 'accounts/login.html')

    if not user_authenticated:
        messages.error(request, f'Usuário ou senha inválidos, tentativas restantes: {LOGIN_TRIES_MAX - tries + 1}')
        return render(request, 'accounts/login.html')
    
    #Realiza o login do usuário e reseta as tentativas de login
    auth.login(request, user_authenticated)
    login_tries = {}
    tries = 1
    return redirect('dashboard')

@receiver(auth.user_logged_in)
def remove_other_sessions(sender, user, request, **kwargs):
    #Derruba a sessão do mesmo usuário anterior
    Session.objects.filter(usersession__user=user).delete()
    
    #Salva a sessão atual
    request.session.save()

    #Cria a sessão atual do usuário
    UserSession.objects.get_or_create(
        user=user,
        session_id=request.session.session_key
    )