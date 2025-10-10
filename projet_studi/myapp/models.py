from django.db import models
from datetime import datetime, timezone
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    pass

GENRE_CHOICES = [
    ('H', 'Homme'),
    ('F', 'Femme'),
]
class Epreuve(models.Model):
    
    date = models.DateField()
    heure = models.TimeField()
    discipline = models.CharField(max_length=100, help_text="Nom du sport, par exemple 'Athletisme', 'Natation' etc..")
    genre = models.CharField(max_length=1, choices=GENRE_CHOICES)
    competition = models.CharField(max_length=50, help_text="Nom de l'épreuve, par exemple 'Finale - 100 mètres")
    tarif = models.DecimalField(max_digits=6, decimal_places=2, help_text="Tarif en euros")

    def __str__(self):
        return f"{self.discipline} - {self.competition} ({self.genre})"