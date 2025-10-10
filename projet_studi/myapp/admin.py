from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(User)

@admin.register(Epreuve)
class EpreuveAdmin(admin.ModelAdmin):
    list_display = ('date', 'heure', 'genre', 'discipline', 'competition', 'tarif')
# admin.site.register(Roles)
# admin.site.register(Users)
# admin.site.register(Offres)
# admin.site.register(Tickets)

