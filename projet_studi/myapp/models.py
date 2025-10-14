from django.db import models
from django.conf import settings
from datetime import datetime, timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError



class User(AbstractUser):
    pass


class Epreuve(models.Model):
    
    GENRE_CHOICES = [
    ('H', 'Homme'),
    ('F', 'Femme'),
]
    
    date = models.DateField()
    heure = models.TimeField()
    discipline = models.CharField(max_length=100, help_text="Nom du sport, par exemple 'Athletisme', 'Natation' etc..")
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    competition = models.CharField(max_length=50, help_text="Nom de l'épreuve, par exemple 'Finale - 100 mètres")
    tarif = models.DecimalField(max_digits=6, decimal_places=2, help_text="Tarif en euros")

    def __str__(self):
        return f"{self.discipline} - {self.competition} ({self.genre})"
    

class Ticket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    epreuve = models.ForeignKey(
        "Epreuve",  # référence au modèle Epreuve
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    quantite = models.PositiveSmallIntegerField(default=1)
    date_achat = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "epreuve")  # un utilisateur ne peut acheter qu'une fois pour une même épreuve

    def __str__(self):
        return f"{self.user.username} - {self.epreuve.nom} ({self.quantite} ticket{'s' if self.quantite > 1 else ''})"

    def clean(self):
        """Valide la quantité de tickets autorisée (1, 2 ou 4 uniquement)."""
        if self.quantite not in [1, 2, 4]:
            raise ValidationError("Vous ne pouvez acheter que 1, 2 ou 4 tickets par épreuve.")

    @property
    def total(self):
        """Calcule le total basé sur le prix de l’épreuve."""
        return self.quantite * self.epreuve.tarif