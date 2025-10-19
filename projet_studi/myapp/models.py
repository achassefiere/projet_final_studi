from django.db import models
from django.conf import settings
from datetime import datetime, timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
import hashlib


# On utilise la classe AbstractUser fournie par Django
class User(AbstractUser):
    pass

# Creation de la table Epreuve et des fonction associées
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
    lieu = models.CharField(max_length=255, default="À définir", help_text="Lieu de l'épreuve")

    def __str__(self):
        return f"{self.discipline} - {self.competition} ({self.genre})"
    

# Creation de la table Ticket et des fonction associées
class Ticket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    epreuve = models.ForeignKey(
        "Epreuve",
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    code = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
        default="temp"
    )
    quantite = models.PositiveSmallIntegerField(default=1)
    date_achat = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "epreuve")

    def __str__(self):
        return f"{self.user.username} - {self.epreuve.nom} ({self.quantite} ticket{'s' if self.quantite > 1 else ''})"

    def clean(self):
        """Valide la quantité autorisée."""
        if self.quantite not in [1, 2, 4]:
            raise ValidationError("Vous ne pouvez acheter que 1, 2 ou 4 tickets par épreuve.")

    @property
    def total(self):
        """Retourne le montant total de l’achat."""
        return self.quantite * self.epreuve.tarif

    def save(self, *args, **kwargs):
        """Génère un code unique sécurisé."""
        if self.code == "temp" or not self.code:
            raw_string = f"{self.user_id}-{self.epreuve_id}"
            self.code = hashlib.sha256(raw_string.encode()).hexdigest()
        super().save(*args, **kwargs)