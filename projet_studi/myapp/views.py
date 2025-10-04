from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader
from django.contrib.auth import authenticate, login, logout
from .forms import LoginForm, SignupForm

from .models import *

def host_view(request: HttpRequest): # accueil du site
    return render(request, 'host.html')

def login_view(request):
    form = LoginForm(request.POST or None)
    message = ''
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('host')  # redirige vers la page d'accueil
            else:
                message = 'Nom d’utilisateur ou mot de passe incorrect.'

    return render(request, 'login.html', {'form': form, 'message': message})

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('login')

    form = SignupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)  # Connexion automatique après inscription
            return redirect('host')
    
    return render(request, 'signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def all_users(request: HttpRequest):
    users = User.objects.all()
    context = {'users': users}
    template = loader.get_template('myapp_templates/users.html')
    return HttpResponse(template.render(context, request))

def one_user(request: HttpRequest, pk: int):
    user = get_object_or_404(User, pk=pk)   
    context = {'user': user}
    template = loader.get_template('myapp_templates/user.html')
    return HttpResponse(template.render(context, request))