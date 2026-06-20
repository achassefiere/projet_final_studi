from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db.models import Q, CheckConstraint
from decimal import Decimal



# On utilise la classe AbstractUser fournie par Django
class User(AbstractUser):
    pass

class Vehicule(models.Model):

    # Mode de commercialisation
    MODE_VENTE = "vente"
    MODE_LOCATION = "location"

    MODE_CHOICES = [
        (MODE_VENTE, "Vente"),
        (MODE_LOCATION, "Location"),
    ]

    # Statut
    STATUT_DISPONIBLE = "disponible"
    STATUT_INDISPONIBLE = "indisponible"

    STATUT_CHOICES = [
        (STATUT_DISPONIBLE, "Disponible"),
        (STATUT_INDISPONIBLE, "Indisponible"),
    ]

    marque = models.CharField("Marque", max_length=100)
    modele = models.CharField("Modèle", max_length=100)
    motorisation = models.CharField("Motorisation", max_length=50, blank=True)
    annee = models.PositiveSmallIntegerField("Année")
    kilometrage = models.PositiveIntegerField("Kilométrage")
    numero_vin = models.CharField("N° VIN", max_length=17, unique=True)

    prix_vente = models.DecimalField(
        "Prix de vente",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    loyer_mensuel = models.DecimalField(
        "Loyer mensuel",
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    mode = models.CharField(
        "Mode",
        max_length=20,
        choices=MODE_CHOICES,
        default=MODE_VENTE,
    )

    statut = models.CharField(
        "Statut",
        max_length=15,
        choices=STATUT_CHOICES,
        default=STATUT_DISPONIBLE,
    )

    photo = models.ImageField(
        "Photo principale",
        upload_to="vehicules/",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehicule"
        verbose_name_plural = "Vehicules"
        ordering = ["-created_at"]

    def clean(self):
        super().clean()

        if self.numero_vin and len(self.numero_vin) != 17:
            raise ValidationError({
                "numero_vin": "Le VIN doit contenir exactement 17 caractères."
            })

        if self.mode == self.MODE_VENTE and not self.prix_vente:
            raise ValidationError({
                "prix_vente": "Le prix de vente est obligatoire pour un véhicule à vendre."
            })

        if self.mode == self.MODE_LOCATION and not self.loyer_mensuel:
            raise ValidationError({
                "loyer_mensuel": "Le loyer mensuel est obligatoire pour un véhicule en location."
            })

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.annee}) – {self.get_mode_display()}"

    def switch_to_location(self):
        self.mode = self.MODE_LOCATION
        self.save(update_fields=["mode", "updated_at"])

    def switch_to_vente(self):
        self.mode = self.MODE_VENTE
        self.save(update_fields=["mode", "updated_at"])
        

class OptionLocation(models.Model):

    code = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix_mensuel = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.label} ({self.prix_mensuel}€)"
 
 
# ──────────────────────────────────────────────
# DOSSIER (achat ou location)
# ──────────────────────────────────────────────

class Dossier(models.Model):
    """Dossier client achat ou location LLD."""

    # =========================
    # TYPES
    # =========================
    TYPE_ACHAT = "achat"
    TYPE_LOCATION = "location"

    TYPE_CHOICES = [
        (TYPE_ACHAT, "Achat"),
        (TYPE_LOCATION, "Location longue durée"),
    ]

    # =========================
    # STATUT
    # =========================
    STATUT_SOUMIS = "soumis"
    STATUT_APPROUVE = "approuve"
    STATUT_REJETE = "rejete"

    STATUT_CHOICES = [
        (STATUT_SOUMIS, "Soumis"),
        (STATUT_APPROUVE, "Approuvé"),
        (STATUT_REJETE, "Refusé"),
    ]

    # =========================
    # RELATIONS
    # =========================
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="dossiers",
    )

    vehicule = models.ForeignKey(
        "Vehicule",
        on_delete=models.CASCADE,
        related_name="dossiers",
    )

    # =========================
    # TYPE + STATUT
    # =========================
    dossier_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMIS)

    # =========================
    # LOCATION
    # =========================
    location_duration_months = models.PositiveSmallIntegerField(null=True, blank=True)

    location_options = models.ManyToManyField(
        OptionLocation,
        blank=True,
        related_name="dossiers"
    )

    # 👉 prix total des options
    location_price = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    # =========================
    # NOTES
    # =========================
    client_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)

    # =========================
    # TIMESTAMPS
    # =========================
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    decided_at = models.DateTimeField(null=True, blank=True)

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_dossiers",
    )

    # =========================
    # VALIDATION
    # =========================
    def clean(self):
        if not self.dossier_type or not self.vehicule:
            return

        mode = self.vehicule.mode

        if self.dossier_type == self.TYPE_ACHAT:
            if mode != "vente":
                raise ValidationError("Ce véhicule n'est pas disponible à l'achat.")

            if self.location_duration_months:
                raise ValidationError("Pas de durée pour un achat.")

        elif self.dossier_type == self.TYPE_LOCATION:
            if mode != "location":
                raise ValidationError("Ce véhicule n'est pas disponible en location.")
            
    @property
    def location_total_price(self):
        return sum(opt.prix_mensuel for opt in self.location_options.all())

    def __str__(self):
        return f"Dossier #{self.pk} - {self.get_dossier_type_display()} - {self.vehicule}"
    
# ──────────────────────────────────────────────
# DOCUMENTS DU DOSSIER
# ──────────────────────────────────────────────
 
class DossierDocument(models.Model):
    """Document dématérialisé joint à un dossier."""
 
    TYPE_ID = "identite"
    TYPE_REVENU = "preuve_revenu"
    TYPE_RESIDENCE = "preuve_residence"
    TYPE_PERMIS_CONDUIRE = "permis_conduire"
    TYPE_BANQUE = "releve_bancaire"
    TYPE_AUTRE = "autre"
 
    TYPE_CHOICES = [
        (TYPE_ID, "Pièce d'identité"),
        (TYPE_REVENU, "Justificatif de revenus"),
        (TYPE_RESIDENCE, "Justificatif de domicile"),
        (TYPE_PERMIS_CONDUIRE, "Permis de conduire"),
        (TYPE_BANQUE, "Relevé bancaire"),
        (TYPE_AUTRE, "Autre"),
    ]
 
    
    dossier = models.ForeignKey(
        Dossier,
        related_name="documents",
        on_delete=models.CASCADE
    )

    document_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    file = models.FileField(upload_to="documents/")
    label = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = "Document du dossier"
        verbose_name_plural = "Documents du dossier"
        ordering = ["uploaded_at"]
 
    def __str__(self):
        return f"{self.get_document_type_display()} – Dossier #{self.dossier_id}"
 
 
# ──────────────────────────────────────────────
# SUIVI / HISTORIQUE DU DOSSIER
# ──────────────────────────────────────────────
 
class DossierStatusHistory(models.Model):
    """Historique des changements de statut d'un dossier."""
 
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name="history")
    statut_precedent = models.CharField("Ancien statut", max_length=20, blank=True)
    nouveau_statut = models.CharField("Nouveau statut", max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Modifié par",
    )
    commentaire = models.TextField("Commentaire", blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = "Historique dossier"
        verbose_name_plural = "Historiques dossiers"
        ordering = ["-changed_at"]
 
    def __str__(self):
        return (
            f"Dossier #{self.dossier_id} : "
            f"{self.statut_precedent or '–'} → {self.nouveau_statut}"
        )
        

class Notification(models.Model):

    TYPE_INFO = "info"
    TYPE_SUCCES = "succes"
    TYPE_AVERTISSEMENT = "avertissement"
    TYPE_ERREUR = "erreur"

    TYPE_CHOICES = [
        (TYPE_INFO, "Information"),
        (TYPE_SUCCES, "Succès"),
        (TYPE_AVERTISSEMENT, "Avertissement"),
        (TYPE_ERREUR, "Erreur"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_INFO)

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]