README - Plateforme d'Évaluation pour les Bases de Données
Banner

📌 Table des Matières
Description du Projet

Fonctionnalités Clés

Technologies Utilisées

Installation

Configuration

Utilisation

Contributeurs

Licence

🚀 Description du Projet
La Plateforme d'Évaluation pour les Bases de Données est une solution complète destinée aux enseignants et étudiants en bases de données relationnelles. Cette plateforme permet :

La création et gestion d'exercices SQL et de modélisation

La soumission et l'évaluation automatisée des travaux

Le suivi des progrès des étudiants

La correction assistée par IA

Public cible : Enseignants et étudiants en informatique, particulièrement dans les domaines des bases de données.

✨ Fonctionnalités Clés
Pour les Professeurs
🎯 Création d'exercices avec différents niveaux de difficulté

📝 Gestion des solutions modèles

🤖 Correction automatique avec feedback IA

📊 Tableaux de bord analytiques

🔔 Système de notifications

Pour les Étudiants
📤 Soumission des travaux en ligne

⚡ Correction instantanée

📈 Visualisation des progrès

🗣️ Possibilité de contestation des notes

🔍 Accès aux feedbacks détaillés

💻 Technologies Utilisées
Backend
Python 3.10+

Django 4.2

Django REST Framework

PostgreSQL (production) / SQLite (développement)

Celery (tâches asynchrones)

Redis (cache et broker)

Frontend
Tailwind CSS

HTMX (interactions dynamiques)

Alpine.js (composants interactifs)

Chart.js (visualisation des données)

Sécurité
Chiffrement AES-256 des fichiers

Journalisation des événements sensibles

Authentification à deux facteurs

🛠️ Installation
Prérequis
Python 3.10+

PostgreSQL (optionnel pour la production)

Redis

Node.js (pour certains assets frontend)

Étapes d'installation
Cloner le dépôt :

bash
Copy
git clone https://github.com/bayembaye/projet-plateforme-db.git
cd projet-plateforme-db
Créer un environnement virtuel :


python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Installer les dépendances :


pip install -r requirements.txt
Configurer la base de données :


python manage.py migrate
Créer un superutilisateur :



python manage.py createsuperuser
Lancer le serveur de développement :



python manage.py runserver
⚙️ Configuration
Copiez le fichier .env.example vers .env et modifiez les paramètres :



# Paramètres critiques
SECRET_KEY=votre-cle-secrete
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Configuration email (pour les notifications)
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
Pour la production, configurez :

DEBUG=False

Une base de données PostgreSQL

Un stockage externe pour les fichiers média

HTTPS obligatoire

🏁 Utilisation
Commandes utiles
Import initial des données :


python manage.py loaddata initial_data.json
Lancer les workers Celery :


celery -A plateforme_evaluation worker -l info
Lancer le serveur :


python manage.py runserver
Accès initial
Interface admin : /admin/

API REST : /api/



👥 Contributeurs
L'équipe de développement :

Awa Lo 

Baye Mbaye Biteye 

Papa Mounirou Seck 

Seynabou Laye Mbaye 

MBaye Ndiaye 

📜 Licence
