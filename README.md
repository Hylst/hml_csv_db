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
- Onglet de requêtes SQL avancées avec présets organisés par catégories :
  - Requêtes générales
  - Analyse par artiste
  - Analyse par album
  - Durée et taille
  - Métadonnées
  - Formats audio
  - Dates
- Possibilité de créer et sauvegarder vos propres requêtes SQL

## Prérequis

- Python 3.6 ou supérieur
- PyQt5
- SQLite3

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

## Licence

Ce projet est sous licence MIT.

## Auteur

Geoffroy Streit
