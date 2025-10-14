from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.host_view, name='host'), # rien entre guillemet = l'URL par défaut du site
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('epreuves/', views.list_epreuves, name='liste_epreuves'),
    path('epreuves/creer/', views.create_epreuve, name='creer_epreuve'),
    path('epreuves/modifier/<int:epreuve_id>/', views.update_epreuve, name='modifier_epreuve'),
    path('epreuves/supprimer/<int:epreuve_id>/', views.delete_epreuve, name='supprimer_epreuve'),
    path('epreuves/<int:epreuve_id>/acheter/', views.buy_ticket, name='acheter_ticket'),
    path('tickets/', views.liste_tickets, name='liste_tickets'),
    path('users', views.all_users),
    path('user/<int:pk>', views.one_user)
]
