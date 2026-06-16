from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.home_view, name='accueil'), # rien entre guillemet = l'URL par défaut du site
    path('login/', views.connexion_view, name='connexion'),
    path('signup/', views.inscription_view, name='inscription'),
    path('logout/', views.deconnexion_view, name='deconnexion'),
    
    # URLS VEHICULES CRUD
    path("vehicules/", views.vehicule_list, name="vehicule_list"),
    path("vehicules/create/", views.vehicule_create, name="vehicule_create"),
    path("vehicules/<int:pk>/update/", views.vehicule_update, name="vehicule_update"),
    path("vehicules/<int:pk>/delete/", views.vehicule_delete, name="vehicule_delete"),
    
    # URLS DOSSIERS CLIENT
    path("dossiers/creer/<int:vehicule_id>/", views.dossier_create, name="dossier_create"),
    path("dossiers/mes-dossiers/", views.mes_dossiers, name="mes_dossiers"),
    path("dossiers/<int:dossier_id>/documents/", views.upload_document, name="upload_document"),
    
    # URLS DOSSIERS ADMIN
    path("admin/dossiers/", views.admin_dossiers_list, name="admin_dossiers_list"),
    path("admin/dossiers/<int:pk>/valider/", views.admin_dossier_valider, name="admin_dossier_valider"),
    path("admin/dossiers/<int:pk>/refuser/", views.admin_dossier_refuser, name="admin_dossier_refuser"),
]
