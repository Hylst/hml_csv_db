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

### Correction
- Correction du bug "no such table: mp3_files" dans l'exécution des requêtes SQL
- Optimisation de l'affichage des données dans le tableau
