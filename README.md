# MP3Tag Analyzer

Analyseur de métadonnées MP3 compatible avec les exports CSV de MP3Tag.

## Description

MP3Tag Analyzer est une application qui permet d'analyser, rechercher et filtrer les métadonnées de vos fichiers MP3 exportées depuis le logiciel MP3Tag. Cette application offre une interface graphique conviviale pour explorer vos collections de musique et obtenir des statistiques détaillées.

## Fonctionnalités

- Importation des fichiers CSV exportés depuis MP3Tag (UTF-8, UTF-16 avec BOM)
- Détection automatique de l'encodage des fichiers
- Stockage des données dans une base SQLite pour des performances optimales
- Interface de recherche avancée (par artiste, album, titre, etc.)
- Tri des données par n'importe quelle colonne
- Onglet de requêtes SQL avancées avec présents organisés par catégories :
  - Requêtes générales
  - Analyse par artiste
  - Analyse par album
  - Durée et taille
  - Métadonnées
  - Formats audio
  - Dates
- Possibilité de créer et sauvegarder vos propres requêtes SQL
- Support flexible des différentes structures de fichiers CSV (colonnes variables, ordre différent)
- Export des données vers des bases de données externes :
  - MySQL
  - PostgreSQL

## Prérequis

- Python 3.6 ou supérieur
- PyQt5
- SQLite3
- Pour l'export MySQL : mysql-connector-python (optionnel)
- Pour l'export PostgreSQL : psycopg2-binary (optionnel)

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers sources
2. Installez les dépendances : `pip install -r requirements.txt`
3. Lancez l'application : `python mp3tag_analyzer.py`

## Utilisation

### Importer un fichier CSV depuis MP3Tag

1. Dans MP3Tag, sélectionnez tous les fichiers que vous souhaitez exporter
2. Allez dans File > Export > Export CSV
3. Choisissez les colonnes que vous voulez exporter
4. Sauvegardez le fichier CSV
5. Dans MP3Tag Analyzer, cliquez sur "Charger CSV" et sélectionnez votre fichier

### Format attendu des fichiers CSV

- Fichiers générés par MP3tag (format par défaut : UTF-16-LE avec BOM)
- Séparateur point-virgule (;)
- L'application supporte également des variantes de structure (ordre des colonnes différent, noms de colonnes variables)

### Rechercher dans vos données

1. Utilisez le champ de recherche en haut de l'application
2. Sélectionnez la colonne dans laquelle rechercher ou "Tous les champs"
3. Appuyez sur Entrée ou cliquez sur "Rechercher"

### Trier vos données

- Cliquez sur l'en-tête d'une colonne pour trier dans l'ordre croissant
- Cliquez à nouveau pour trier dans l'ordre décroissant

### Exécuter des requêtes SQL

1. Allez dans l'onglet "Requêtes SQL"
2. Sélectionnez une catégorie et un preset existant, ou écrivez votre propre requête
3. Cliquez sur "Exécuter"
4. Les résultats s'affichent dans l'onglet "Données"

### Exporter vers MySQL ou PostgreSQL

1. Chargez d'abord un fichier CSV ou une base de données SQLite
2. Dans le menu Fichier, allez dans "Exporter vers..." et choisissez MySQL ou PostgreSQL
3. Configurez les paramètres de connexion dans la boîte de dialogue
4. Cliquez sur OK pour lancer l'exportation

## Améliorations prévues

### Fonctionnalités d'analyse avancée
- Visualisations graphiques (répartition par genre, artistes les plus représentés)
- Analyse de tendances (années les plus représentées, évolution des genres)
- Détection des doublons

### Améliorations de l'interface
- Thèmes personnalisables (mode clair/sombre)
- Interface responsive
- Raccourcis clavier avancés

### Améliorations techniques
- Cache des requêtes SQL
- Export vers plus de formats (CSV, JSON, XML)
- Synchronisation cloud

### Gestion de métadonnées
- Édition groupée
- Normalisation des métadonnées
- Enrichissement de données via API musicales

## Documentation

Une documentation complète est disponible dans les fichiers suivants :
- `help.md` : Aide intégrée de l'application
- `DOCUMENTATION.md` : Documentation technique et guide utilisateur

## Licence

Ce projet est sous licence MIT.

## Auteur

Geoffroy Streit
