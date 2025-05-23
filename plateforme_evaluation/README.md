# README - Plateforme d'Évaluation pour les Bases de Données

# 📌 Table des Matières
- [Description du Projet](#-description-du-projet)
- [Fonctionnalités Clés](#-fonctionnalités-clés)
- [Technologies Utilisées](#-technologies-utilisées)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Manuel Utilisateur](#-manuel-utilisateur)
  - [Première Connexion](#première-connexion)
  - [Interface Étudiant](#interface-étudiant)
  - [Interface Enseignant](#interface-enseignant)
  - [Soumission d'un Travail](#soumission-dun-travail)
  - [Correction Automatique](#correction-automatique)
  - [Détection de Plagiat](#détection-de-plagiat)
  - [Gestion des Notifications](#gestion-des-notifications)
  - [FAQ](#faq)
- [Contributeurs](#-contributeurs)
- [Licence](#-licence)

# 🚀 Description du Projet
La Plateforme d'Évaluation pour les Bases de Données est une solution complète destinée aux enseignants et étudiants en bases de données relationnelles. Cette plateforme permet :

- La création et gestion d'exercices SQL et de modélisation
- La soumission et l'évaluation automatisée des travaux
- Le suivi des progrès des étudiants
- La correction assistée par IA

Public cible : Enseignants et étudiants en informatique, particulièrement dans les domaines des bases de données.

# ✨ Fonctionnalités Clés

# Pour les Professeurs
- 🎯 Création d'exercices avec différents niveaux de difficulté
- 📝 Gestion des solutions modèles
- 🤖 Correction automatique avec feedback IA
- 📊 Tableaux de bord analytiques
- 🔔 Système de notifications

# Pour les Étudiants
- 📤 Soumission des travaux en ligne
- ⚡ Correction instantanée
- 📈 Visualisation des progrès
- 🗣️ Possibilité de contestation des notes
- 🔍 Accès aux feedbacks détaillés

# 💻 Technologies Utilisées

# Backend
- Python 3.10+
- Django 4.2
- Django REST Framework
- PostgreSQL (production) / SQLite (développement)
- Celery (tâches asynchrones)
- Redis (cache et broker)

# Frontend
- Tailwind CSS
- HTMX (interactions dynamiques)
- Alpine.js (composants interactifs)
- Chart.js (visualisation des données)

# Sécurité
- Chiffrement AES-256 des fichiers
- Journalisation des événements sensibles
- Authentification à deux facteurs

# 🛠️ Installation

# Prérequis
- Python 3.10+
- PostgreSQL (optionnel pour la production)
- Redis
- Node.js (pour certains assets frontend)

# Étapes d'installation
1. Cloner le dépôt :
```bash
git clone https://github.com/bayembaye/projet-plateforme-db.git
cd projet-plateforme-db
```

2. Créer un environnement virtuel :
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

4. Configurer la base de données :
```bash
python manage.py migrate
```

5. Créer un superutilisateur :
```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :
```bash
python manage.py runserver
```

# ⚙️ Configuration
Copiez le fichier .env.example vers .env et modifiez les paramètres :

```
# Paramètres critiques
SECRET_KEY=votre-cle-secrete
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

# Configuration email (pour les notifications)
EMAIL_HOST=smtp.votre-fournisseur.com
EMAIL_PORT=587
EMAIL_HOST_USER=votre@email.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe
```

Pour la production, configurez :
- DEBUG=False
- Une base de données PostgreSQL
- Un stockage externe pour les fichiers média
- HTTPS obligatoire

# 🏁 Utilisation

# Commandes utiles
- Import initial des données :
```bash
python manage.py loaddata initial_data.json
```

- Lancer les workers Celery :
```bash
celery -A plateforme_evaluation worker -l info
```

- Lancer le serveur :
```bash
python manage.py runserver
```

# Accès initial
- Interface admin : `/admin/`
- API REST : `/api/`

# 📖 Manuel Utilisateur

# Première Connexion

# Création de compte
- Rendez-vous sur `/account/signup/`
- Choisissez votre rôle (Étudiant ou Enseignant)
- Complétez les informations requises
- Validez votre email via le lien reçu

# Connexion initiale
- Accédez à `/account/login/`
- Utilisez vos identifiants ou les options d'authentification externes
- Complétez votre profil après la première connexion

# Interface Étudiant

# Tableau de Bord
- **Exercices disponibles** : Liste des travaux à rendre
- **Progression** : Graphique de vos résultats et évolution
- **Dernières notes** : Feedback récents
- **Statistiques personnelles** : Visualisation des performances par matière
- **Comparaison avec la classe** : Positionnement par rapport à la moyenne

# Suivi des Performances
- Visualisation des soumissions passées
- Historique complet des notes obtenues
- Performances par rapport à chaque exercice
- Comparaison avec la moyenne de la classe
- Diagramme de feedback
- Avancée par catégorie d'exercices
- Identification des points forts et axes d'amélioration

# Fonctionnalités Clés
- Soumission de fichiers (SQL, PDF, DOCX) avec support Drag & Drop
- Consultation des corrections automatiques
- Analyse des performances par catégorie avec graphiques d'évolution
- Possibilité de contester une note avec justification détaillée
- Accès aux sujets déposés par les professeurs
- Modification des soumissions avant la date limite

# Interface Enseignant

# Gestion des Comptes
- Création et gestion des comptes enseignants
- Définition des droits d'accès

# Création et Gestion d'Exercices
1. Cliquez sur "Nouvel Exercice"
2. Renseignez :
   - Titre et description
   - Niveau de difficulté
   - Fichiers ressources
   - Dépôt de sujets en format texte/PDF
   - Ajout de plusieurs modèles de correction pour chaque exercice
3. Définissez la date limite
4. Possibilité de modifier l'exercice après publication :
   - Mise à jour des consignes
   - Ajout de ressources supplémentaires
   - Extension de la date limite

# Correction des Copies
- Liste des soumissions à corriger
- Interface de notation avec :
  - Barème sur 20 points
  - Zone de feedback détaillé
  - Suggestions automatiques d'IA
  - Possibilité d'ajuster les notes générées par l'IA
- Traitement des contestations de notes des étudiants

# Tableau de Bord Enseignant
- Statistiques détaillées des performances des étudiants :
  - Top des étudiants par exercice/module
  - Tendances des soumissions (horaires, fréquence)
  - Nombre total de soumissions
  - Nombre d'exercices créés
  - Moyenne de la classe par exercice
  - Taux de complétion des exercices
- Analyse des erreurs fréquentes :
  - Erreurs se répétant souvent
  - Concepts mal assimilés par la classe
- Graphique des performances pour chaque exercice
- Rapports exportables au format PDF/Excel

# Soumission d'un Travail
1. Sélectionnez l'exercice
2. Cliquez sur "Soumettre"
3. Téléversez votre fichier (glisser-déposer supporté)
4. Ajoutez un commentaire (optionnel)
5. Confirmez la soumission
6. Possibilité de modifier sa soumission tant que la date limite n'est pas dépassée

> **Attention :** Les soumissions après la date limite sont marquées comme tardives

# Correction Automatique

# Analyse de l'IA
- La syntaxe SQL
- La structure des requêtes
- La conformité avec l'énoncé
- La performance des requêtes
- La correspondance avec les modèles de correction fournis

# Résultats
- Note indicative
- Feedback détaillé
- Suggestions d'amélioration
- Comparaison avec les solutions idéales

# Détection de Plagiat

# Fonctionnement du Système Anti-Plagiat
- Analyse automatique de chaque soumission
- Comparaison avec :
  - Base de données interne de travaux précédents
  - Sources disponibles sur le web
  - Autres soumissions du même exercice
- Score de similarité exprimé en pourcentage
- Types de scan disponibles : interne, web, ou les deux

# Interprétation des Résultats
- **0-15%** : Similarité normale, pas d'inquiétude
- **15-40%** : Similarité modérée, vérification recommandée
- **40-100%** : Similarité élevée, investigation nécessaire

# Interface de Vérification
- Accès aux détails du scan via l'icône "Voir"
- Relancer un scan avec l'icône "Actualiser"
- Visualisation des correspondances internes détectées
- Consultation des correspondances web (si disponibles)
- Accès aux données techniques du scan

> **Attention :** Un score de similarité de 100% indique un plagiat potentiel nécessitant une attention immédiate

# Gestion des Notifications

# Types de notifications
- Nouvel exercice disponible
- Soumission notée

# Actions possibles
- Marquer comme lu
- Accéder directement à l'élément concerné

# FAQ

*Q : Puis-je modifier ma soumission après l'avoir envoyée ?**  
R : Oui, tant que la date limite de l'exercice n'est pas dépassée. Cliquez sur "Modifier la soumission" depuis la page de l'exercice.

*Q : Comment contester une note ?**  
R : Allez dans la page de la soumission et cliquez sur "Contester". Rédigez une justification claire expliquant pourquoi vous pensez mériter une autre note.

**Q : Les corrections automatiques sont-elles définitives ?**  
R : Non, elles servent d'aide aux enseignants qui ont toujours le dernier mot.

**Q : Quels formats de fichiers sont acceptés pour les soumissions ?**  
R : SQL, PDF et DOCX principalement. D'autres formats peuvent être acceptés selon les paramètres définis par l'enseignant.

**Q : Comment suivre ma progression sur le long terme ?**  
R : Le tableau de bord étudiant propose des graphiques d'évolution, des statistiques par matière et une comparaison avec la moyenne de la classe.

**Q : Un enseignant peut-il modifier un exercice après sa publication ?**  
R : Oui, les enseignants peuvent mettre à jour les consignes, ajouter des ressources et même prolonger la date limite.

> Pour toute autre question, contactez l'équipe du projet.

# 👥 Contributeurs
L'équipe de développement :

- Awa Lo 
- Baye Mbaye Biteye 
- Papa Mounirou Seck 
- Seynabou Laye Mbaye 
- MBaye Ndiaye 

 📜 Licence
