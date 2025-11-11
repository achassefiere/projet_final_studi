from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from .models import *
from datetime import datetime

# Page d'accueil du site
def accueil_view(request):
    prochaines_epreuves = Epreuve.objects.filter(
        date__gte=datetime.now()
    ).order_by('date', 'heure')[:3]

    return render(request, 'accueil.html', {
        'prochaines_epreuves': prochaines_epreuves
    })

# Connexion d'un utilisateur
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

# Inscription d'un nouvel utilisateur
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

# Déconnexion de l'utilisateur
def deconnexion_view(request):
    logout(request)
    return redirect('accueil')

# Création d'une épreuve
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

# Modification d'une épreuve
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

# Accès a la liste des épreuves avec pagination
def liste_epreuves(request):
    epreuves_list = Epreuve.objects.all().order_by('date', 'heure')
    paginator = Paginator(epreuves_list, 10)  # 🔹 10 résultats par page

    page_number = request.GET.get('page')
    epreuves = paginator.get_page(page_number)

    return render(request, 'liste_epreuves.html', {'epreuves': epreuves})

# Accès au détail d'une épreuve
def detail_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    return render(request, 'detail_epreuve.html', {'epreuve': epreuve})

# Suppression d'une épreuve
def supprimer_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    
    if request.method == 'POST':
        epreuve.delete()  # supprime l'épreuve et tous les tickets liés
        return redirect('liste_epreuves')
    
    return redirect('liste_epreuves')

# Formulaire d'achat d'un, de deux ou de quatre tickets
def acheter_ticket(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)

    # Vérifie si l’utilisateur a déjà acheté un ticket pour cette épreuve
    already_bought = Ticket.objects.filter(user=request.user, epreuve=epreuve).exists()

    total = None
    form = None

    if already_bought:
        messages.warning(request, "Vous avez déjà acheté des tickets pour cette épreuve.")
    else:
        form = BuyTicketForm(request.POST or None)

        if request.method == 'POST' and form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.epreuve = epreuve

            # Valide uniquement la quantité sans exécuter full_clean complet
            ticket.clean()  # vérifie que la quantité = 1,2 ou 4

            # Génération et sauvegarde du code unique dans save()
            ticket.save()

            total = ticket.total
            messages.success(
                request,
                f"Achat réussi ! Vous avez acheté {ticket.quantite} billet{'s' if ticket.quantite > 1 else ''} "
                f"pour un total de {total:.2f} €."
            )

            # Redirige vers la page des billets
            return redirect('liste_tickets')

    context = {
        'form': form,
        'epreuve': epreuve,
        'total': total,
        'already_bought': already_bought,
    }

    return render(request, 'acheter_ticket.html', context)

# Accès a la liste des tickets de l'utilisateur avec pagination
def liste_tickets(request):
    tickets_list = Ticket.objects.filter(user=request.user).order_by('-date_achat')

    # Création du paginateur
    paginator = Paginator(tickets_list, 10)  # 10 tickets par page
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    return render(request, 'liste_tickets.html', {'tickets': tickets})

# Accès a la liste de tous les tickets avec pagination
def liste_tickets_admin(request):
    # Seuls les admins peuvent voir tous les tickets
    if not request.user.is_staff:
        messages.error(request, "Accès refusé. Cette page est réservée aux administrateurs.")
        return redirect('accueil')

    # Récupération de tous les tickets avec jointures
    tickets_list = Ticket.objects.select_related('user', 'epreuve').order_by('-date_achat')

    # Pagination - 10 tickets par page
    paginator = Paginator(tickets_list, 10)
    page_number = request.GET.get('page')
    tickets = paginator.get_page(page_number)

    return render(request, 'liste_tickets_admin.html', {'tickets': tickets})

# Suppression d'une épreuve
def supprimer_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        ticket.delete()  # supprime l'épreuve et tous les tickets liés
        return redirect('liste_tickets_admin')