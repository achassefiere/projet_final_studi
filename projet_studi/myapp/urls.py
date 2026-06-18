from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home_view, name='accueil'), # rien entre guillemet = l'URL par défaut du site
    path('login/', views.connexion_view, name='connexion'),
    path('signup/', views.inscription_view, name='inscription'),
    path('logout/', views.deconnexion_view, name='deconnexion'),
    
    # URLS VEHICULES CRUD
    path("vehicules/", views.vehicule_list, name="vehicule_list"),
    path("vehicules/<int:pk>/", views.vehicule_detail, name="vehicule_detail"),
    path("vehicules/create/", views.vehicule_create, name="vehicule_create"),
    path("vehicules/<int:pk>/update/", views.vehicule_update, name="vehicule_update"),
    path("vehicules/<int:pk>/delete/", views.vehicule_delete, name="vehicule_delete"),
    
    # URLS DOSSIERS CLIENT
    path("dossiers/creer/<int:vehicule_id>/", views.dossier_create, name="dossier_create"),
    path("dossiers/mes-dossiers/", views.mes_dossiers, name="mes_dossiers"),
    path("dossiers/<int:dossier_id>/documents/", views.upload_document, name="upload_document"),
    
    # URLS DOSSIERS ADMIN
    path("backoffice/dossiers/", views.dossier_list, name="dossier_list"),
    path("backoffice/dossiers/<int:pk>/", views.dossier_detail, name="dossier_detail"),
    path("backoffice/dossiers/<int:pk>/valider/", views.dossier_valider, name="dossier_valider"),
    path("backoffice/dossiers/<int:pk>/refuser/", views.dossier_refuser, name="dossier_refuser"),
]
