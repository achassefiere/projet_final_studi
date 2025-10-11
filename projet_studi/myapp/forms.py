from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import Epreuve, GENRE_CHOICES

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
    def validate_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les deux mots de passe ne correspondent pas.")
        return password2
    
    # Sauvegarde de l'utilisateur 
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])  # Hachage du password afin qu'il n'apparaisse pas en clair dans la BDD
        if commit:
            user.save()
        return user
        

class CreateEpreuveForm(forms.ModelForm):
    
    genre = forms.ChoiceField(choices=GENRE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = Epreuve
        fields = ['date', 'heure', 'genre', 'discipline', 'competition', 'tarif']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'discipline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Athlétisme, Natation, Cyclisme'
            }),
            'competition': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Finale Femme 200m nage libre'
            }),
            'tarif': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }