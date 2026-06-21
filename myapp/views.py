import zipfile, logging
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
from io import BytesIO
from .services import *


logger = logging.getLogger(__name__)

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

# Pas de @login_required pour les tests
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

    if vehicule.statut != Vehicule.STATUT_DISPONIBLE:
        return render(request, "error.html", {
            "message": "Ce véhicule n'est plus disponible."
        })

    form = DossierForm(request.POST or None)

    print("METHOD:", request.method)

    if request.method == "POST":
        print("FORM VALID:", form.is_valid())
        print("ERRORS:", form.errors)

    if request.method == "POST" and form.is_valid():

        dossier = form.save(commit=False)

        # IMPORTANT : type dossier (corrige bug "Type vide")
        dossier.dossier_type = (
            Dossier.TYPE_LOCATION
            if vehicule.mode == "location"
            else Dossier.TYPE_ACHAT
        )

        dossier.client = request.user
        dossier.vehicule = vehicule
        dossier.statut = Dossier.STATUT_SOUMIS
        dossier.submitted_at = timezone.now()

        dossier.save()

        # 🔗 ManyToMany
        options = form.cleaned_data.get("location_options") or []
        dossier.location_options.set(options)

        return redirect("upload_document", dossier_id=dossier.pk)

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

    dossier = get_object_or_404(Dossier, pk=dossier_id)
    documents = dossier.documents.all()

    if request.method == "POST":

        form = DossierDocumentForm(request.POST, request.FILES)

        if form.is_valid():

            document_type = form.cleaned_data["document_type"]

            # limite 1 type par dossier
            if documents.filter(document_type=document_type).exists():
                form.add_error("document_type", "Ce type de document existe déjà.")

            # add max 5 documents
            elif documents.count() >= 5:
                form.add_error(None, "Maximum 5 documents atteints.")

            else:
                doc = form.save(commit=False)
                doc.dossier = dossier   # 🔥 liaison obligatoire
                doc.save()
                
                print("DOC ID:", doc.id)
                print("DOSSIER ID:", doc.dossier_id)
                print("DOSSIER OBJ:", dossier.id)

                return redirect("upload_document", dossier_id=dossier.pk)

    else:
        form = DossierDocumentForm()

    return render(request, "upload_document.html", {
        "form": form,
        "dossier": dossier,
        "documents": documents,
    })
    
@login_required
def document_valider(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    # 🔒 sécurité accès
    if request.user != dossier.client and not request.user.is_staff:
        return redirect("accueil")

    # 📎 vérifie documents liés au dossier
    if not dossier.documents.exists():
        return redirect("upload_document", dossier_id=dossier.pk)

    # 🔥 validation
    dossier.statut = Dossier.STATUT_SOUMIS
    dossier.save()

    return redirect("mes_dossiers")
    
@login_required
def dossier_detail(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    # 🔒 sécurité : client OU admin uniquement
    if not request.user.is_staff and dossier.client != request.user:
        return redirect("accueil")

    # 📎 récupération des documents liés
    documents = dossier.documents.all()

    return render(request, "dossier_detail.html", {
        "dossier": dossier,
        "documents": documents
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

    # 🔥 Mise à jour dossier
    dossier.statut = Dossier.STATUT_APPROUVE
    dossier.decided_at = timezone.now()
    dossier.reviewed_by = request.user
    dossier.save()

    # 🚗 mise à jour véhicule (disponible / indisponible)
    update_vehicule_status(dossier.vehicule)

    return redirect("dossier_list")

@user_passes_test(is_admin)
def dossier_refuser(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    # Mise à jour dossier
    dossier.statut = Dossier.STATUT_REJETE
    dossier.decided_at = timezone.now()
    dossier.reviewed_by = request.user
    dossier.save()

    # mise à jour véhicule
    update_vehicule_status(dossier.vehicule)

    # NOTIFICATION CLIENT
    Notification.objects.create(
        user=dossier.client,
        title="Dossier refusé",
        message="Votre dossier a été refusé.",
        type="error"
    )

    return redirect("dossier_list")

@login_required
def dossier_delete(request, pk):

    dossier = get_object_or_404(Dossier, pk=pk)

    if request.user != dossier.client and not request.user.is_staff:
        return redirect("accueil")

    vehicule = dossier.vehicule

    if request.method == "POST":
        dossier.delete()

        # recalcul statut véhicule
        from .services import update_vehicule_status
        update_vehicule_status(vehicule)

        return redirect("mes_dossiers")

    return render(request, "dossier_confirm_delete.html", {
        "dossier": dossier
    })
    
@login_required
def download_dossier(request, dossier_id):

    dossier = get_object_or_404(Dossier, pk=dossier_id)

    # sécurité : client ou staff uniquement
    if request.user != dossier.client and not request.user.is_staff:
        return HttpResponse("Accès interdit", status=403)

    buffer = BytesIO()

    with zipfile.ZipFile(buffer, "w") as zip_file:

        for doc in dossier.documents.all():

            if doc.file:
                zip_file.writestr(
                    doc.file.name.split("/")[-1],
                    doc.file.read()
                )

    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/zip")
    response["Content-Disposition"] = f'attachment; filename="dossier_{dossier.id}.zip"'

    return response
