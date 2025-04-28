from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, Http404

from .models import *

def first_view(request: HttpRequest):
    return HttpResponse("hello world !")

def all_users(request: HttpRequest):
    users = Users.objects.all()
    return HttpResponse(users)

def one_user(request: HttpRequest, pk: int):
    user = get_object_or_404(Users, pk=pk)   
    return HttpResponse(user)