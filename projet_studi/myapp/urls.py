from django.urls import path, include
from .views import first_view, all_users, one_user


urlpatterns = [
    path('hello', first_view),
    path('users', all_users),
    path('users/<int:pk>', one_user)
]
