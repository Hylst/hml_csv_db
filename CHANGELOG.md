# Journal des modifications

## v1.0.0 (23/03/2025)

### Ajout
- Première version fonctionnelle de l'application
- Interface graphique en PyQt5
- Chargement de fichiers CSV générés par MP3tag
- Affichage des données dans un tableau
- Stockage des données dans une base SQLite
- Fonction de recherche basique

## v1.1.0 (23/03/2025)

### Ajout
- Détection automatique de l'encodage des fichiers CSV (UTF-8, UTF-16-LE avec BOM)
- Support des séparateurs point-virgule et virgule
- Traitement asynchrone des fichiers volumineux
- Amélioration de la journalisation des erreurs

### Correction
- Résolution des problèmes de chargement des fichiers CSV avec encodage UTF-16
- Amélioration de la détection des en-têtes du fichier CSV

## v1.2.0 (23/03/2025)

### Ajout
- Système de mapping entre les noms de colonnes CSV (CamelCase) et ceux de la base de données (snake_case)
- Correction des problèmes d'insertion dans la base de données
- Isolation des opérations SQLite dans des threads séparés pour éviter les erreurs de threading

### Correction
- Résolution du problème "SQLite objects created in a thread can only be used in that same thread"
- Amélioration de la gestion des erreurs lors de l'insertion des données

## v1.3.0 (23/03/2025)

### Ajout
- Tri des données par colonne (clic sur l'en-tête)
- Amélioration du système de recherche pour prendre en compte tous les formats de noms de colonnes
- Nouvel onglet de requêtes SQL avec présets organisés par catégories:
  - Requêtes générales
  - Analyse par artiste
  - Analyse par album
  - Durée et taille
  - Métadonnées
  - Formats audio
  - Dates
- Possibilité de créer et sauvegarder ses propres requêtes SQL avec choix de catégorie
- Support de différentes structures de fichiers CSV (colonnes variables, ordre différent)
- Amélioration de la détection et normalisation des en-têtes de colonnes
- Gestion plus robuste des importations avec validation dynamique des colonnes

### Correction
- Correction du bug "no such table: mp3_files" dans l'exécution des requêtes SQL
- Optimisation de l'affichage des données dans le tableau
- Résolution des problèmes d'importation qui faisaient que le programme se figeait avec certains fichiers CSV
- Correction des problèmes de requêtes SQL qui ne renvoyaient aucun résultat
- Améliorations du processus d'importation pour tolérer des structures de colonnes différentes

## v1.4.0 (23/03/2025)

### Ajout
- Fonctionnalité d'export vers des bases de données externes:
  - Support de MySQL via mysql-connector-python
  - Support de PostgreSQL via psycopg2
- Interface de configuration des paramètres de connexion aux bases de données
- Traitement asynchrone des exports pour éviter le blocage de l'interface

### Correction
- Correction du problème de sauvegarde de la base de données qui n'enregistrait pas les données
- Amélioration de la gestion des erreurs lors de l'exportation
- Optimisation du processus d'enregistrement de la base de données

## v1.5.0 (23/03/2025)

### Ajout
- Fonctionnalité d'export vers des formats de fichiers standards:
  - Export vers CSV avec options de configuration (séparateur, encodage, en-têtes)
  - Export vers JSON avec options de format (tableau ou objet avec IDs)
  - Export vers XML avec options de personnalisation (noms d'éléments, formatage)
- Interface utilisateur pour la configuration des options d'export
- Traitement asynchrone des exports pour maintenir la réactivité de l'interface

### Amélioration
- Meilleure gestion des erreurs lors des exports
- Options d'encodage étendues pour une meilleure compatibilité avec d'autres applications
- Préservation des métadonnées lors de l'export vers différents formats

## v1.6.0 (24/03/2025)

### Ajout
- Possibilité d'édition directe des données dans le tableau
- Boutons de réinitialisation des filtres et des données
- Menu de configuration de la largeur des colonnes avec 4 modes (automatique, minimal, moyen, large)

### Amélioration
- Conversion automatique du temps AudioLength en format heures:minutes:secondes
- Affichage du nombre d'éléments exportés dans les messages de confirmation
- Boîte de dialogue "À propos" enrichie avec plus de détails sur les fonctionnalités
- Meilleure gestion de l'affichage des données dans le tableau
