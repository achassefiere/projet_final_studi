from django.urls import path, include
from .views import host_view, login_view, signup_view, logout_view, all_users, one_user


urlpatterns = [
    path('', host_view, name='host'), # rien entre guillemet = l'URL par défaut du site
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('users', all_users),
    path('user/<int:pk>', one_user)
]
