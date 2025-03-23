# Documentation MP3Tag Analyzer

## Table des matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Architecture du programme](#architecture-du-programme)
4. [Fonctionnalités](#fonctionnalités)
5. [Interface utilisateur](#interface-utilisateur)
6. [Formats de données](#formats-de-données)
7. [Base de données](#base-de-données)
8. [Export vers bases externes](#export-vers-bases-externes)
9. [Bonnes pratiques](#bonnes-pratiques)
10. [Dépannage](#dépannage)
11. [Développement futur](#développement-futur)

## Introduction

MP3Tag Analyzer est une application Python conçue pour analyser, rechercher et filtrer les métadonnées de fichiers MP3 exportées depuis le logiciel MP3Tag. Cette application offre une interface graphique conviviale pour explorer des collections musicales et obtenir des statistiques détaillées.

Cette documentation est destinée aux utilisateurs finaux ainsi qu'aux développeurs souhaitant comprendre ou étendre les fonctionnalités de l'application.

## Installation

### Prérequis

- Python 3.6 ou supérieur
- Dépendances Python listées dans `requirements.txt`

### Installation standard

1. Clonez le dépôt ou téléchargez les fichiers sources
2. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```
3. Lancez l'application :
   ```
   python mp3tag_analyzer.py
   ```

### Dépendances optionnelles

Pour utiliser les fonctionnalités d'export vers des bases de données externes, installez les modules suivants :

- Pour MySQL :
  ```
  pip install mysql-connector-python
  ```
- Pour PostgreSQL :
  ```
  pip install psycopg2-binary
  ```

### Installation pour le développement

Pour contribuer au développement :

1. Créez un environnement virtuel :
   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```
2. Installez les dépendances de développement :
   ```
   pip install -r requirements-dev.txt  # Si disponible
   ```

## Architecture du programme

L'application est structurée selon une architecture modulaire avec séparation des responsabilités :

### Modules principaux

- **mp3tag_analyzer.py** : Point d'entrée de l'application
- **gui.py** : Interface graphique et logique d'interaction utilisateur
- **csv_parser.py** : Analyse et traitement des fichiers CSV
- **db_manager.py** : Gestion de la base de données SQLite
- **db_exporter.py** : Export vers MySQL et PostgreSQL

### Flux de données

1. L'utilisateur charge un fichier CSV via l'interface graphique
2. Le parser CSV analyse le fichier et extrait les données
3. Les données sont stockées dans une base SQLite temporaire ou permanente
4. L'interface affiche les données et permet leur manipulation
5. Optionnellement, les données peuvent être exportées vers MySQL ou PostgreSQL

### Diagramme de classes simplifié

```
MainWindow (gui.py)
  ├── CSVParser (csv_parser.py)
  ├── DatabaseManager (db_manager.py)
  └── DBExporter (db_exporter.py)
```

### Threads et asynchronicité

L'application utilise des threads séparés pour les opérations longues afin de maintenir la réactivité de l'interface :

- Chargement de fichiers CSV volumineux
- Insertion de données dans la base
- Exécution de requêtes SQL complexes
- Export vers bases de données externes

La classe `Worker` (dans gui.py) encapsule cette logique de threading.
