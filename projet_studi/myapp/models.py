from django.db import models
from datetime import datetime, timezone

# Create your models here.
class Roles(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    mail = models.EmailField(unique=True)
    key = models.CharField(max_length=255, unique=True) ## a verifier
    password = models.CharField(max_length=255)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    
class Offres(models.Model):
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True) ## a verifier
    time = models.TimeField(auto_now=False, auto_now_add=False, blank=True, null=True) ## a verifier
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
class Tickets(models.Model):
    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=255, unique=True) ## a verifier
    concat_key = models.CharField(max_length=255, unique=True) ## a verifier
    offre = models.ForeignKey(Offres, on_delete=models.CASCADE)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    ## a finir

## add class Panier ??