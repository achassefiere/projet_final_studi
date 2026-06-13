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
    
    # MODE pour MODE DE COMMERCIALISATION
    # valeurs stockées en base de données
    MODE_VENTE = "vente"
    MODE_LOCATION = "location"
    MODE_LES_DEUX = "les_deux"

    # constantes
    MODE_CHOICES = [
        (MODE_VENTE, "Vente"),
        (MODE_LOCATION, "Location"),
        (MODE_LES_DEUX, "Vente & Location"),
    ]
    
    STATUT_DISPONIBLE = "disponible"
    STATUT_LOUE = "loue"
    STATUT_VENDU = "vendu"
    STATUT_INDISPONIBLE = "indisponible"

    STATUT_CHOICES = [
        (STATUT_DISPONIBLE, "Disponible"),
        (STATUT_LOUE, "Loué"),
        (STATUT_VENDU, "Vendu"),
        (STATUT_INDISPONIBLE, "Indisponible"),
    ]
    
    marque = models.CharField("Marque", max_length=100)
    modele = models.CharField("Modèle", max_length=100)
    motorisation = models.CharField("Motorisation", max_length=50, blank=True)
    annee = models.PositiveSmallIntegerField("Année")
    kilometrage = models.PositiveIntegerField("Kilométrage")
    numero_vin = models.CharField("N° VIN", max_length=17, unique=True) # VEHICLE IDENTIFICATION NUMBER
    
    prix_vente = models.DecimalField(
        "Prix de vente",
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    loyer_mensuel = models.DecimalField(
        "Loyer mensuel",
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    
    mode = models.CharField("Mode", max_length=20, choices=MODE_CHOICES, default=MODE_VENTE)
    statut = models.CharField("Statut", max_length=15, choices=STATUT_CHOICES, default=STATUT_DISPONIBLE)
    photo = models.ImageField("Photo principale", upload_to="vehicules/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"
        ordering = ["-created_at"]
        
    def clean(self):
        super().clean()
        if self.numero_vin and len(self.numero_vin) != 17:
            raise ValidationError({
                "numero_vin": "Le VIN doit contenir exactement 17 caractères."
            })
 
    def __str__(self):
        return f"{self.marque} {self.modele} ({self.annee}) – {self.get_mode_display()}"
 
    def switch_to_location(self):
        """Basculer le véhicule en mode location."""
        self.mode = self.MODE_LOCATION
        self.save(update_fields=["mode", "updated_at"])
 
    def switch_to_vente(self):
        """Basculer le véhicule en mode vente."""
        self.mode = self.MODE_VENTE
        self.save(update_fields=["mode", "updated_at"])

class VehiculePhoto(models.Model):
    """Photos additionnelles d'un véhicule."""
 
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField("Image", upload_to="vehicules/galerie/")
    caption = models.CharField("Légende", max_length=255, blank=True)
    order = models.PositiveSmallIntegerField("Ordre", default=0)
 
    class Meta:
        verbose_name = "Photo vehicule"
        verbose_name_plural = "Photos vehicule"
        ordering = ["order"]
 
    def __str__(self):
        return f"Photo #{self.pk} – {self.vehicule}"
 
 
# ──────────────────────────────────────────────
# OPTIONS DE LOCATION (LLD)
# ──────────────────────────────────────────────
 
class OptionLocation(models.Model):
    """Option disponible dans un abonnement de location longue durée."""
 
    CODE_TOUS_RISQUES = "tous_risques"
    CODE_DEPANNAGE = "depannage"
    CODE_MAINTENANCE = "maintenance"
    CODE_CT = "controle_technique"
 
    CODE_CHOICES = [
        (CODE_TOUS_RISQUES, "Assurance tous risques"),
        (CODE_DEPANNAGE, "Assistance depannage"),
        (CODE_MAINTENANCE, "Entretien & SAV"),
        (CODE_CT, "Contrôle technique"),
    ]
 
    code = models.CharField("Code", max_length=30, unique=True, choices=CODE_CHOICES)
    label = models.CharField("Libellé", max_length=100)
    description = models.TextField("Description", blank=True)
    prix_mensuel = models.DecimalField(
        "Prix mensuel (€)",
        max_digits=8, decimal_places=2,
        default=Decimal("0.00"),
    )
    is_included = models.BooleanField(
        "Incluse dans l'abonnement",
        default=False,
        help_text="Si cochée, l'option est offerte sans supplément.",
    )
 
    class Meta:
        verbose_name = "Option de location"
        verbose_name_plural = "Options de location"
 
    def __str__(self):
        tag = "incluse" if self.is_included else f"{self.prix_mensuel} €/mois"
        return f"{self.label} ({tag})"
 
 
# ──────────────────────────────────────────────
# DOSSIER (achat ou location)
# ──────────────────────────────────────────────
 
class Dossier(models.Model):
    """Dossier déposé par un client pour un achat ou une location LLD."""
 
    TYPE_ACHAT = "achat"
    TYPE_LOCATION = "location"
 
    TYPE_CHOICES = [
        (TYPE_ACHAT, "Achat"),
        (TYPE_LOCATION, "Location longue durée"),
    ]
 
    STATUT_BROUILLON = "brouillon"
    STATUT_SOUMIS = "submitted"
    STATUT_EN_COURS = "under_review"
    STATUT_APPROUVE = "approved"
    STATUT_REJETE = "rejected"
    STATUT_ANNULE = "cancelled"
 
    STATUT_CHOICES = [
        (STATUT_BROUILLON, "Brouillon"),
        (STATUT_SOUMIS, "Soumis"),
        (STATUT_EN_COURS, "En cours d'examen"),
        (STATUT_APPROUVE, "Approuvé"),
        (STATUT_REJETE, "Refusé"),
        (STATUT_ANNULE, "Annulé"),
    ]
 
    # Relations
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="dossiers",
        verbose_name="Client",
    )
    vehicule = models.ForeignKey(
        Vehicule,
        on_delete=models.PROTECT,
        related_name="dossiers",
        verbose_name="Véhicule",
    )
 
    # Type & état
    dossier_type = models.CharField("Type", max_length=20, choices=TYPE_CHOICES)
    statut = models.CharField("Statut", max_length=20, choices=STATUT_CHOICES, default=STATUT_BROUILLON)
 
    # Options LLD choisies (uniquement pour TYPE_LOCATION)
    location_options = models.ManyToManyField(
        OptionLocation,
        blank=True,
        verbose_name="Options choisies",
    )
 
    # Durée pour la LLD
    location_duration_months = models.PositiveSmallIntegerField(
        "Durée (mois)",
        null=True, blank=True,
        help_text="Applicable uniquement pour une location LLD.",
    )
 
    # Remarques
    client_notes = models.TextField("Notes du client", blank=True)
    staff_notes = models.TextField("Notes internes", blank=True)
 
    # Horodatage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField("Soumis le", null=True, blank=True)
    decided_at = models.DateTimeField("Décidé le", null=True, blank=True)
 
    # Agent qui a traité le dossier
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="reviewed_dossiers",
        verbose_name="Traité par",
    )
 
    class Meta:
        verbose_name = "Dossier"
        verbose_name_plural = "Dossiers"
        ordering = ["-created_at"]
        
    def clean(self):
        super().clean()
        
        if not self.dossier_type:
            raise ValidationError({
                "dossier_type": "Le type de dossier est obligatoire."
            })

        if not self.vehicule:
            raise ValidationError({
                "vehicule": "Un véhicule est obligatoire."
            })

        # Achat
        if self.dossier_type == self.TYPE_ACHAT:

            if self.location_duration_months:
                raise ValidationError({
                    "location_duration_months": "La durée n'est autorisée que pour une location."
                })

            if self.vehicule.mode == Vehicule.MODE_LOCATION:
                raise ValidationError({
                    "vehicule": "Ce véhicule est uniquement disponible en location."
                })

        # Location
        elif self.dossier_type == self.TYPE_LOCATION:

            if self.vehicule.mode == Vehicule.MODE_VENTE:
                raise ValidationError({
                    "vehicule": "Ce véhicule est uniquement disponible à la vente."
                })
    
    def save(self, *args, **kwargs):
        if not kwargs.get("raw", False):
            self.full_clean()
        super().save(*args, **kwargs)
 
    def __str__(self):
        return (
            f"Dossier #{self.pk} – {self.get_dossier_type_display()} – "
            f"{self.vehicule} – {self.client}"
        )
 
    @property
    def is_location(self):
        return self.dossier_type == self.TYPE_LOCATION
 
    @property
    def is_achat(self):
        return self.dossier_type == self.TYPE_ACHAT
 
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
 
    dossier = models.ForeignKey(Dossier, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField("Type de document", max_length=20, choices=TYPE_CHOICES)
    file = models.FileField("Fichier", upload_to="dossiers/documents/")
    label = models.CharField("Nom du fichier", max_length=255, blank=True)
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
 
 
# ──────────────────────────────────────────────
# CONTRAT (généré après approbation)
# ──────────────────────────────────────────────
 
class Contrat(models.Model):
    """Contrat généré suite à l'approbation d'un dossier."""
 
    dossier = models.OneToOneField(Dossier, on_delete=models.PROTECT, related_name="contrat")
    numero_contrat = models.CharField("N° contrat", max_length=50, unique=True)
    date_debut = models.DateField("Date de début")
    date_fin = models.DateField("Date de fin", null=True, blank=True)
    signed_by_client = models.BooleanField("Signé par le client", default=False)
    signed_at = models.DateTimeField("Signé le", null=True, blank=True)
    document = models.FileField("Document contractuel", upload_to="contrats/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        verbose_name = "Contrat"
        verbose_name_plural = "Contrats"
 
    def __str__(self):
        return f"Contrat {self.numero_contrat} – {self.dossier}"
