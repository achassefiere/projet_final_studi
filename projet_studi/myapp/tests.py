from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import *
from django.utils import timezone

User = get_user_model()

class VehiculeTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.vehicule = Vehicule.objects.create(
            marque="Toyota",
            modele="Yaris",
            motorisation="Essence",
            annee=2020,
            kilometrage=50000,
            numero_vin="12345678901234567",
            mode="vente",
            prix_vente=15000,
            statut="disponible"
        )

    # -------------------------
    # CREATE
    # -------------------------
    def test_create_vehicule(self):
        response = self.client.post(reverse("vehicule_create"), {
            "marque": "Peugeot",
            "modele": "206",
            "motorisation": "Diesel",
            "annee": 2022,
            "kilometrage": 10000,
            "numero_vin": "11111111111111111",
            "mode": "vente",
            "prix_vente": 12000,
            "statut": "disponible"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicule.objects.count(), 2)

    # -------------------------
    # UPDATE
    # -------------------------
    def test_update_vehicule(self):
        url = reverse("vehicule_update", args=[self.vehicule.pk])

        response = self.client.post(url, {
            "marque": "Toyota",
            "modele": "Yaris GR",
            "motorisation": "Essence",
            "annee": 2021,
            "kilometrage": 60000,
            "numero_vin": self.vehicule.numero_vin,
            "mode": "vente",
            "prix_vente": 20000,
            "statut": "disponible"
        })

        self.vehicule.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.vehicule.modele, "Yaris GR")

    # -------------------------
    # DELETE
    # -------------------------
    def test_delete_vehicule(self):
        url = reverse("vehicule_delete", args=[self.vehicule.pk])

        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Vehicule.objects.count(), 0)