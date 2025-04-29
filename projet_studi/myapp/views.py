from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader

from .models import *

def first_view(request: HttpRequest):
    return HttpResponse("hello world !")

def all_users(request: HttpRequest):
    users = Users.objects.all()
    context = {'users': users}
    template = loader.get_template('myapp_templates/users.html')
    return HttpResponse(template.render(context, request))

def one_user(request: HttpRequest, pk: int):
    user = get_object_or_404(Users, pk=pk)   
    context = {'user': user}
    template = loader.get_template('myapp_templates/user.html')
    return HttpResponse(template.render(context, request))