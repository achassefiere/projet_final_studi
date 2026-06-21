from .models import Dossier, Vehicule


def update_vehicule_status(vehicule):
    
    # Met à jour le statut du véhicule selon les dossiers approuvés.
    # Vérifie s'il existe au moins un dossier approuvé pour ce véhicule
    has_approved = Dossier.objects.filter(
        vehicule=vehicule,
        statut=Dossier.STATUT_APPROUVE
    ).exists()

    # Mise à jour du statut véhicule
    if has_approved:
        vehicule.statut = Vehicule.STATUT_INDISPONIBLE
    else:
        vehicule.statut = Vehicule.STATUT_DISPONIBLE

    vehicule.save(update_fields=["statut"])