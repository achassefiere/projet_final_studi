from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Entrez un mot de passe"
        })
    )
    password2 = forms.CharField(
        label="Confirmez le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': "Confirmez votre mot de passe"
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            "username": "Nom d'utilisateur",
            "email": "Adresse email",
            "password1": "Mot de passe",
            "password2": "Confirmation du mot de passe",
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "Nom d'utilisateur"
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "Adresse email"
            }),
        }
    
    # Validation de l'email    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Exemple : vérifier que l'email est unique
        if User.objects.filter(email=email).exists():
            raise ValidationError("Cette adresse email est déjà utilisée.")
        # Exemple : vérifier un domaine spécifique (optionnel)
        return email

    # Validation des deux mots de passe s'ils sont identiques
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError("Les deux mots de passe ne correspondent pas.")

        return cleaned_data
    
    # Sauvegarde de l'utilisateur 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Hachage du password afin qu'il n'apparaisse pas en clair dans la BDD
        if commit:
            user.save()
        return user
        

class VehiculeForm(forms.ModelForm):

    class Meta:
        model = Vehicule
        fields = [
            "marque",
            "modele",
            "motorisation",
            "annee",
            "kilometrage",
            "numero_vin",
            "mode",
            "prix_vente",
            "loyer_mensuel",
            "statut",
            "photo",
        ]

        widgets = {
            "marque": forms.TextInput(attrs={"class": "form-control"}),
            "modele": forms.TextInput(attrs={"class": "form-control"}),
            "motorisation": forms.TextInput(attrs={"class": "form-control"}),
            "annee": forms.NumberInput(attrs={"class": "form-control"}),
            "kilometrage": forms.NumberInput(attrs={"class": "form-control"}),
            "numero_vin": forms.TextInput(attrs={"class": "form-control"}),
            "mode": forms.Select(attrs={"class": "form-select"}),
            "prix_vente": forms.NumberInput(attrs={"class": "form-control"}),
            "loyer_mensuel": forms.NumberInput(attrs={"class": "form-control"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
        
class DossierForm(forms.ModelForm):
    class Meta:
        model = Dossier
        fields = [
            "location_duration_months",
            "client_notes",
        ]
        
class DossierDocumentForm(forms.ModelForm):
    class Meta:
        model = DossierDocument
        fields = ["document_type", "file", "label"]