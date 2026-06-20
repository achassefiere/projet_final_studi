from django.contrib import admin
from .models import *

# -------------------------
# USER ADMIN
# -------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_staff", "is_superuser", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")

# -------------------------
# VEHICULE ADMIN
# -------------------------
@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):

    # colonnes affichées dans la liste
    list_display = (
        "marque",
        "modele",
        "annee",
        "mode",
        "statut",
        "kilometrage",
        "prix_vente",
        "loyer_mensuel",
    )

    # filtres sur le côté droit
    list_filter = (
        "mode",
        "statut",
        "annee",
        "marque",
    )

    # recherche dans la barre admin
    search_fields = (
        "marque",
        "modele",
        "numero_vin",
    )

    # ordre par défaut
    ordering = ("-created_at",)

    # champs en lecture seule
    readonly_fields = ("created_at", "updated_at")
    
