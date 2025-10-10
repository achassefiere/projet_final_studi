from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Epreuve, GENRE_CHOICES

User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur", max_length=150)
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput)
    

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse e-mail")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        

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