from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from .models import *

def host_view(request: HttpRequest): # accueil du site
    return render(request, 'host.html')

def login_view(request):
    form = LoginForm(request.POST or None)
    message = ''
    
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('host')  # redirige vers la page d'accueil
            else:
                message = 'Nom d’utilisateur ou mot de passe incorrect.'

    return render(request, 'login.html', {'form': form, 'message': message})


def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Votre compte a été créé avec succès")
            return redirect('host')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = SignupForm()
    
    return render(request, "signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect('host')

def create_epreuve(request):
    if request.method == 'POST':
        form = CreateEpreuveForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Épreuve créée avec succès.")
            return redirect('liste_epreuves')  # ou autre vue de ton choix
    else:
        form = CreateEpreuveForm()
    return render(request, 'creer_epreuve.html', {'form': form})

def update_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)

    if request.method == 'POST':
        form = CreateEpreuveForm(request.POST, instance=epreuve)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Épreuve modifiée avec succès.")
            return redirect('liste_epreuves')
    else:
        form = CreateEpreuveForm(instance=epreuve)

    return render(request, 'update_epreuve.html', {'form': form, 'epreuve': epreuve})

def list_epreuves(request):
    epreuves = Epreuve.objects.all().order_by('date', 'heure')
    return render(request, 'list_epreuves.html', {'epreuves': epreuves})

def delete_epreuve(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)
    
    if request.method == 'POST':
        epreuve.delete()
        return redirect('liste_epreuves')  # ou nom de ta vue liste
    return redirect('liste_epreuves')


def buy_ticket(request, epreuve_id):
    epreuve = get_object_or_404(Epreuve, id=epreuve_id)

    # Vérifie si l’utilisateur a déjà acheté un ticket pour cette épreuve
    if Ticket.objects.filter(user=request.user, epreuve=epreuve).exists():
        messages.warning(request, "Vous avez déjà acheté des tickets pour cette épreuve.")
        return redirect('detail_epreuve', epreuve_id=epreuve.id)

    if request.method == 'POST':
        form = BuyTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.epreuve = epreuve
            ticket.save()
            messages.success(request, f"Achat réussi ! Total : {ticket.total} €")
            return redirect('detail_epreuve', epreuve_id=epreuve.id)
    else:
        form = BuyTicketForm()

    total = None
    if request.method == 'POST' and form.is_valid():
        total = form.cleaned_data['quantite'] * epreuve.tarif

    context = {
        'form': form,
        'epreuve': epreuve,
        'total': total,
    }
    return render(request, 'achat_ticket.html', context)

def liste_tickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'list_tickets.html', {'tickets': tickets})



def all_users(request: HttpRequest):
    users = User.objects.all()
    context = {'users': users}
    template = loader.get_template('myapp_templates/users.html')
    return HttpResponse(template.render(context, request))

def one_user(request: HttpRequest, pk: int):
    user = get_object_or_404(User, pk=pk)   
    context = {'user': user}
    template = loader.get_template('myapp_templates/user.html')
    return HttpResponse(template.render(context, request))