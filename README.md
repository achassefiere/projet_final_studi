# 🚀 Lancer le projet Django avec MySQL

Ce guide explique comment lancer le projet Django depuis GitHub avec une base de données MySQL, étape par étape.  

---

## 1️⃣ Prérequis

Avant de commencer, assurez-vous d’avoir installé :  

- [Python 3.11+](https://www.python.org/downloads/)  
- [MySQL Community Server](https://dev.mysql.com/downloads/mysql/)  
- `pip` et `virtualenv`  
- Git  
- (Optionnel) Un éditeur de code comme VS Code ou PyCharm  

---

## 2️⃣ Cloner le projet


```bash
git clone https://github.com/<ton-utilisateur>/<nom-du-repo>.git
cd <nom-du-repo>
```

## 3️⃣ Créer et activer un environnement virtuel

# Créer un environnement virtuel
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

## 4️⃣ Installer les dépendances
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Assurez-vous que requirements.txt contient au moins :
```ini
Django==5.0.4
mysqlclient==2.1.1
python-decouple==3.8
dj-database-url==1.0.0
django-widget-tweaks==1.5.0
```

## 5️⃣ Configurer MySQL

Connectez vous a MySQL :
```bash
mysql -u root -p
```

Créez la base de données :
```bash
CREATE DATABASE projet_studi_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
```
(Optionnel) Créez un utilisateur dédié : 
```bash   
CREATE USER 'mon_user'@'localhost' IDENTIFIED BY 'mon_motdepasse';
GRANT ALL PRIVILEGES ON projet_studi_db.* TO 'mon_user'@'localhost';
FLUSH PRIVILEGES;
```

## 6️⃣ Configurer le fichier .env
À la racine du projet (au même niveau que manage.py), créez un fichier .env :
```ini
SECRET_KEY=mettez_votre_cle_secrete
DEBUG=True
DB_NAME=projet_studi_db
DB_USER=root
DB_PASSWORD=123+Aze!
DB_HOST=localhost
DB_PORT=3306
```

Remplacez les valeurs par celles correspondant à votre environnement.

## 7️⃣ Appliquer les migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## 8️⃣ Créer un super utilisateur (optionnel)
```bash
python manage.py createsuperuser
```

Suivez ensuite les instructions pour créer un compte admin.

## 9️⃣ Lancer le serveur

```bash
python manage.py runserver
```
Le projet sera accessible ici : http://127.0.0.1:8000

## Astuces et dépannage

- Variables None : assurez-vous que toutes les variables .env sont correctement définies.

- Erreur MySQL : vérifiez le nom de la base, l’utilisateur et le mot de passe dans .env.

- Fichiers statiques : si besoin pour le déploiement, utilisez :
```bash 
python manage.py collectstatic
```

- Désactiver l’environnement virtuel :
```bash 
deactivate
```