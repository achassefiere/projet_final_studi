from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, Http404
from django.template import loader
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.core.paginator import Paginator
from .forms import *
from .models import *
from datetime import datetime
from django.http import HttpResponse

def is_admin(user):
    return user.is_staff

# Page d'accueil du site
def home_view(request):

    vehicules_recents = Vehicule.objects.all()[:6]

    dossiers_user = None
    dossiers_admin = None

    if request.user.is_authenticated:

        if request.user.is_staff:
            dossiers_admin = Dossier.objects.select_related("vehicule", "client") \
                                           .order_by("-created_at")[:3]
        else:
            dossiers_user = Dossier.objects.filter(client=request.user)

    return render(request, "accueil.html", {
        "vehicules_recents": vehicules_recents,
        "dossiers_user": dossiers_user,
        "dossiers_admin": dossiers_admin,
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

@login_required
def vehicule_create(request):
    if request.method == "POST":
        form = VehiculeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("vehicule_list")
    else:
        form = VehiculeForm()

    return render(request, "vehicule_form.html", {
        "form": form,
        "title": "Créer un véhicule"
    })
    
@login_required
def vehicule_update(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)

    if request.method == "POST":
        form = VehiculeForm(
            request.POST,
            request.FILES,
            instance=vehicule
        )

        if form.is_valid():
            form.save()
            return redirect("vehicule_list")

    else:
        form = VehiculeForm(instance=vehicule)

    return render(request, "vehicule_form.html", {
        "form": form,
        "vehicule": vehicule,
    })

def vehicule_delete(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)

    if request.method == "POST":
        vehicule.delete()
        return redirect("vehicule_list")

    return render(request, "vehicule_confirm_delete.html", {"vehicule": vehicule})

def vehicule_list(request):
    
    mode = request.GET.get("mode")
    vehicules = Vehicule.objects.all().order_by("-created_at")

    if mode:
        vehicules = vehicules.filter(mode=mode)

    paginator = Paginator(vehicules, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "vehicule_list.html", {
        "page_obj": page_obj,
        "mode": mode
    })

def vehicule_detail(request, pk):
    vehicule = get_object_or_404(Vehicule, pk=pk)
    form = VehiculeForm(instance=vehicule)

    for field in form.fields.values():
        field.disabled = True

    return render(request, "vehicule_detail.html", {
        "form": form,
        "vehicule": vehicule,
        "readonly": True
    })

@login_required
def dossier_create(request, vehicule_id):
    vehicule = get_object_or_404(Vehicule, pk=vehicule_id)

    if request.method == "POST":
        form = DossierForm(request.POST)

        if form.is_valid():
            dossier = form.save(commit=False)

            dossier.client = request.user
            dossier.vehicule = vehicule

            if vehicule.mode == Vehicule.MODE_VENTE:
                dossier.dossier_type = Dossier.TYPE_ACHAT
            else:
                dossier.dossier_type = Dossier.TYPE_LOCATION

            dossier.save()

            # ✅ BON NAME ICI
            return redirect("upload_document", dossier_id=dossier.id)

    else:
        form = DossierForm()

    return render(request, "dossier_form.html", {
        "form": form,
        "vehicule": vehicule
    })
    
@login_required
def mes_dossiers(request):
    dossiers = Dossier.objects.filter(client=request.user)

    return render(request, "mes_dossiers.html", {
        "dossiers": dossiers
    })


@login_required
def upload_document(request, dossier_id):
    dossier = get_object_or_404(
        Dossier,
        pk=dossier_id,
        client=request.user  # 🔥 sécurité + évite crash
    )

    if request.method == "POST":
        form = DossierDocumentForm(request.POST, request.FILES)

        if form.is_valid():
            doc = form.save(commit=False)
            doc.dossier = dossier
            doc.save()

            return redirect("mes_dossiers")

        else:
            print(form.errors)  # debug

    else:
        form = DossierDocumentForm()

    return render(request, "document_upload.html", {
        "form": form,
        "dossier": dossier
    })
    
@login_required
def dossier_detail(request, pk):
    dossier = get_object_or_404(Dossier, pk=pk)

    return render(request, "dossier_detail.html", {
        "dossier": dossier
    })
    
@user_passes_test(is_admin)
def dossier_list(request):

    statut = request.GET.get("statut")

    dossiers = Dossier.objects.all().order_by("-created_at")  # tri par date DESC

    if statut:
        dossiers = dossiers.filter(statut=statut)

    # PAGINATION (10 par page)
    paginator = Paginator(dossiers, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "dossier_list.html", {
        "page_obj": page_obj,
        "statut": statut
    })

@user_passes_test(is_admin)
def dossier_valider(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    dossier.statut = Dossier.STATUT_APPROUVE
    dossier.decided_at = timezone.now()
    dossier.reviewed_by = request.user
    dossier.save()

    return redirect("admin_dossiers_list")

@user_passes_test(is_admin)
def dossier_refuser(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    dossier.statut = Dossier.STATUT_REJETE
    dossier.decided_at = timezone.now()
    dossier.reviewed_by = request.user
    dossier.save()

    return redirect("admin_dossiers_list")