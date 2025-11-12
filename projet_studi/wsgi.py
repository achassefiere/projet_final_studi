import os
import sys

# Ajouter le chemin vers ton projet
project_path = '/home/antoinec/projet_final_studi'
if project_path not in sys.path:
    sys.path.append(project_path)

# Définir le settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projet_studi.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()