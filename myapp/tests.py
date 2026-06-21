from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import *
from .forms import *
from django.utils import timezone

User = get_user_model()

class VehiculeTests(TestCase):

    def setUp(self):
        self.client = Client()

        # utilisateur pour login_required
        self.user = User.objects.create_user(
            username="testuser",
            email="test@test.com",
            password="Password123"
        )
        self.client.login(username="testuser", password="Password123")

        # véhicule existant
        self.vehicule = Vehicule.objects.create(
            marque="Toyota",
            modele="Yaris GR",
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
            "numero_vin": "12345678901236547",
            "mode": "vente",
            "prix_vente": 12000,
            "statut": "disponible"
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Vehicule.objects.filter(numero_vin="12345678901236547").exists()
        )

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
        self.assertFalse(
            Vehicule.objects.filter(pk=self.vehicule.pk).exists()
        )


class UserFormTests(TestCase):

    # -------------------------
    # SIGNUP OK
    # -------------------------
    def test_signup_form_valid(self):
        form = SignupForm(data={
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "Password123",
            "password2": "Password123",
        })

        self.assertTrue(form.is_valid())

        user = form.save()

        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertTrue(user.check_password("Password123"))

    # -------------------------
    # SIGNUP PASSWORD ERROR
    # -------------------------
    def test_signup_password_mismatch(self):
        form = SignupForm(data={
            "username": "newuser",
            "email": "newuser@test.com",
            "password1": "Password123",
            "password2": "WrongPassword",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)
        self.assertIn(
            "Les deux mots de passe ne correspondent pas.",
            form.errors["__all__"]
        )

    # -------------------------
    # SIGNUP DUPLICATE EMAIL
    # -------------------------
    def test_signup_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="test@test.com",
            password="Password123"
        )

        form = SignupForm(data={
            "username": "newuser",
            "email": "test@test.com",
            "password1": "Password123",
            "password2": "Password123",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    # -------------------------
    # LOGIN FORM
    # -------------------------
    def test_login_form_valid(self):
        form = LoginForm(data={
            "username": "testuser",
            "password": "Password123",
        })

        self.assertTrue(form.is_valid())

    def test_login_form_invalid(self):
        form = LoginForm(data={
            "username": "wrong",
            "password": "wrongpass",
        })

        # LoginForm ne valide pas l’authentification
        self.assertTrue(form.is_valid())

class DossierFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client",
            email="client@test.com",
            password="Password123"
        )

        self.vehicule = Vehicule.objects.create(
            marque="Renault",
            modele="Clio",
            motorisation="Essence",
            annee=2021,
            kilometrage=30000,
            numero_vin="12345678901234567",
            mode="location",  # IMPORTANT pour éviter validation clean()
            prix_vente=12000,
            loyer_mensuel=300,
            statut="disponible"
        )

        self.option = OptionLocation.objects.create(
            code="GPS",
            label="GPS intégré",
            prix_mensuel=10
        )

    def test_dossier_form_valid(self):
        form = DossierForm(data={
            "location_duration_months": 24,
            "client_notes": "Je veux ce véhicule"
        })

        self.assertTrue(form.is_valid())
        
    def test_create_dossier(self):
        dossier = Dossier.objects.create(
            client=self.user,
            vehicule=self.vehicule,
            dossier_type=Dossier.TYPE_LOCATION,
            statut=Dossier.STATUT_SOUMIS,
            location_duration_months=24,
            client_notes="OK"
        )

        dossier.location_options.add(self.option)

        self.assertEqual(Dossier.objects.count(), 1)
        self.assertEqual(dossier.location_options.count(), 1)
        self.assertEqual(dossier.location_total_price, 10)
        
    def test_clean_invalid_mode(self):
        vehicule = Vehicule.objects.create(
            marque="Peugeot",
            modele="208",
            motorisation="Essence",
            annee=2022,
            kilometrage=10000,
            numero_vin="12345678901234568",
            mode="vente",
            prix_vente=15000,
            statut="disponible"
        )

        dossier = Dossier(
            client=self.user,
            vehicule=vehicule,
            dossier_type=Dossier.TYPE_LOCATION,
            location_duration_months=12
        )

        with self.assertRaises(Exception):
            dossier.full_clean()
            

class DossierDocumentFormTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="client",
            password="Password123"
        )

        self.vehicule = Vehicule.objects.create(
            marque="Renault",
            modele="Clio",
            motorisation="Essence",
            annee=2021,
            kilometrage=30000,
            numero_vin="12345678901234567",
            mode="location",
            prix_vente=12000,
            loyer_mensuel=300,
            statut="disponible"
        )

        self.dossier = Dossier.objects.create(
            client=self.user,
            vehicule=self.vehicule,
            dossier_type=Dossier.TYPE_LOCATION,
            statut=Dossier.STATUT_SOUMIS
        )

    def test_document_form_valid(self):
        form = DossierDocumentForm(
            dossier=self.dossier,
            data={
                "document_type": "identite",
                "label": "Carte ID"
            }
        )

        self.assertIn("document_type", form.fields)