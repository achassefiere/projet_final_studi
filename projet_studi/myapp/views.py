from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .forms import *
from .models import *
from datetime import datetime

prochaines_epreuves = Epreuve.objects.filter(
    date__gte=datetime.now()
).order_by('date', 'heure')[:3]

def accueil_view(request):
    prochaines_epreuves = Epreuve.objects.filter(
        date__gte=datetime.now()
    ).order_by('date', 'heure')[:3]

    return render(request, 'accueil.html', {
        'prochaines_epreuves': prochaines_epreuves
    })

def connexion_view(request):
    form = LoginForm(request.POST or None)
    message = ''
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('accueil')  # redirige vers la page d'accueil
            else:
                message = 'Nom d’utilisateur ou mot de passe incorrect.'

    return render(request, 'connexion.html', {'form': form, 'message': message})


def inscription_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès")
            return redirect('accueil')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = SignupForm()
    
    return render(request, "inscription.html", {"form": form})


def deconnexion_view(request):
    logout(request)
    return redirect('accueil')

def creer_epreuve(request):
    if request.method == 'POST':
        form = CreateEpreuveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Épreuve créée avec succès.")
            return redirect('liste_epreuves')  # ou autre vue de ton choix
    else:
        form = CreateEpreuveForm()
    return render(request, 'creer_epreuve.html', {'form': form})

def editer_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)

    if request.method == 'POST':
        form = CreateEpreuveForm(request.POST, instance=epreuve)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Épreuve modifiée avec succès.")
            return redirect('liste_epreuves')
    else:
        form = CreateEpreuveForm(instance=epreuve)

    return render(request, 'editer_epreuve.html', {'form': form, 'epreuve': epreuve})

def liste_epreuves(request):
    epreuves = Epreuve.objects.all().order_by('date', 'heure')
    return render(request, 'liste_epreuves.html', {'epreuves': epreuves})

def detail_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    return render(request, 'detail_epreuve.html', {'epreuve': epreuve})

def supprimer_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    
    if request.method == 'POST':
        epreuve.delete()
        return redirect('liste_epreuves')  # ou nom de ta vue liste
    return redirect('liste_epreuves')

def acheter_ticket(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)

    # Vérifie si l’utilisateur a déjà acheté un ticket
    already_bought = Ticket.objects.filter(user=request.user, epreuve=epreuve).exists()

    total = None  # Total du ticket
    form = None   # Formulaire initialisé plus bas si nécessaire

    if already_bought:
        messages.warning(request, "Vous avez déjà acheté des tickets pour cette épreuve.")
    else:
        # Initialise le formulaire avec POST ou vide
        form = BuyTicketForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.epreuve = epreuve
            ticket.save()

            total = form.cleaned_data['quantite'] * epreuve.tarif
            messages.success(request, f"Achat réussi ! Total : {total} €")

            # Optionnel : masquer le formulaire après achat
            form = None
            already_bought = True  # Pour désactiver le formulaire après achat

    context = {
        'form': form,
        'epreuve': epreuve,
        'total': total,
        'already_bought': already_bought,
    }

    return render(request, 'acheter_ticket.html', context)

def liste_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'liste_tickets.html', {'tickets': tickets})