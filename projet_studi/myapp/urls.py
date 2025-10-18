from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.accueil_view, name='accueil'), # rien entre guillemet = l'URL par défaut du site
    path('login/', views.connexion_view, name='connexion'),
    path('signup/', views.inscription_view, name='inscription'),
    path('logout/', views.deconnexion_view, name='deconnexion'),
    path('epreuves/', views.liste_epreuves, name='liste_epreuves'),
    path('epreuves/creer/', views.creer_epreuve, name='creer_epreuve'),
    path('epreuves/modifier/<int:epreuve_id>/', views.editer_epreuve, name='editer_epreuve'),
    path('epreuves/supprimer/<int:epreuve_id>/', views.supprimer_epreuve, name='supprimer_epreuve'),
    path('epreuves/detail_epreuve/<int:epreuve_id>/', views.detail_epreuve, name='detail_epreuve'),
    path('epreuves/acheter/<int:epreuve_id>/', views.acheter_ticket, name='acheter_ticket'),
    path('tickets/', views.liste_tickets, name='liste_tickets'),
]
