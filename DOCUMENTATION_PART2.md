# Documentation MP3Tag Analyzer - Partie 2

## Fonctionnalitu00e9s

### Importation de donnu00e9es

#### Import CSV

L'application est spu00e9cialement conu00e7ue pour traiter les fichiers CSV gu00e9nu00e9ru00e9s par MP3Tag :

- **Formats supportu00e9s** :
  - UTF-16-LE avec BOM (format par du00e9faut de MP3Tag)
  - UTF-8
  - Du00e9tection automatique de l'encodage
- **Su00e9parateurs** :
  - Point-virgule (;) - format par du00e9faut de MP3Tag
  - Virgule (,)
- **Structure** :
  - Support flexible des diffu00e9rentes structures de colonnes
  - Normalisation automatique des noms de colonnes
  - Mapping entre les noms de colonnes CSV (CamelCase) et ceux de la base de donnu00e9es (snake_case)

#### Import depuis base de donnu00e9es

L'application peut charger des donnu00e9es depuis des fichiers SQLite existants :

- Ouverture de bases cru00e9u00e9es pru00e9cu00e9demment avec l'application
- Vu00e9rification de la compatibilitu00e9 du schu00e9ma

### Recherche et filtrage

- **Recherche simple** :
  - Recherche par terme dans une colonne spu00e9cifique ou tous les champs
  - Recherche insensible u00e0 la casse
- **Tri** :
  - Tri ascendant/descendant par colonne
  - Tri multiple non supportu00e9 actuellement

### Requu00eates SQL

- **u00c9diteur de requu00eates** :
  - Interface pour u00e9crire des requu00eates SQL personnalisu00e9es
  - Exu00e9cution asynchrone des requu00eates
- **Pru00e9sets** :
  - Requu00eates pru00e9du00e9finies organisu00e9es par catu00e9gories
  - Possibilitu00e9 de sauvegarder des requu00eates personnalisu00e9es

### Export de donnu00e9es

- **SQLite** :
  - Sauvegarde des donnu00e9es dans un fichier SQLite
  - Portabilitu00e9 et ru00e9utilisation
- **MySQL** :
  - Export vers une base MySQL
  - Configuration des paramu00e8tres de connexion
  - Cru00e9ation automatique des tables
- **PostgreSQL** :
  - Export vers une base PostgreSQL
  - Configuration des paramu00e8tres de connexion
  - Cru00e9ation automatique des tables

## Interface utilisateur

### Fenu00eatre principale

L'interface principale est divisu00e9e en plusieurs zones :

- **Barre de menu** : Accu00e8s aux fonctionnalitu00e9s principales
- **Barre d'outils** : Accu00e8s rapide aux actions fru00e9quentes
- **Zone de recherche** : Filtrage des donnu00e9es
- **Onglets** : Navigation entre les diffu00e9rentes vues
  - Onglet Donnu00e9es : Affichage tabulaire des donnu00e9es
  - Onglet Requu00eates SQL : Interface pour les requu00eates personnalisu00e9es
- **Barre de statut** : Informations sur l'u00e9tat de l'application

### Bou00eetes de dialogue

- **Chargement CSV** : Su00e9lection d'un fichier CSV u00e0 importer
- **Chargement/Sauvegarde BDD** : Su00e9lection d'un fichier SQLite
- **Configuration MySQL** : Paramu00e8tres de connexion MySQL
- **Configuration PostgreSQL** : Paramu00e8tres de connexion PostgreSQL
- **u00c0 propos** : Informations sur l'application

### Raccourcis clavier

- **Ctrl+O** : Ouvrir un fichier CSV
- **Ctrl+D** : Ouvrir une base de donnu00e9es
- **Ctrl+S** : Sauvegarder la base de donnu00e9es
- **Ctrl+Q** : Quitter l'application
- **Ctrl+F** : Focus sur le champ de recherche
- **F5** : Rafrau00eechir les donnu00e9es

## Formats de donnu00e9es

### Format CSV attendu

L'application est optimisu00e9e pour les fichiers CSV gu00e9nu00e9ru00e9s par MP3Tag :

```
Title;Artist;Album;Year;Genre;Comment;Length;Size;LastModified;Path
"Titre 1";"Artiste 1";"Album 1";"2020";"Rock";"";"03:45";"9.8 MB";"2023-01-15 14:30:22";"C:\Music\fichier1.mp3"
```

Les colonnes typiques incluent :
- Title, Artist, Album, Year, Genre, Comment
- Track, Disc, Publisher, Composer, BPM
- Length, Size, LastModified, Path
- ISRC, Copyright, Encoder, Rating

L'application peut gu00e9rer des variations dans les noms et l'ordre des colonnes gru00e2ce u00e0 son systu00e8me de normalisation et de mapping.

### Structure de la base de donnu00e9es

La base SQLite utilise principalement une table `mp3_tags` avec des colonnes correspondant aux mu00e9tadonnu00e9es MP3 :

```sql
CREATE TABLE IF NOT EXISTS mp3_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    artist TEXT,
    album TEXT,
    year TEXT,
    genre TEXT,
    comment TEXT,
    track TEXT,
    disc TEXT,
    publisher TEXT,
    composer TEXT,
    length TEXT,
    size TEXT,
    path TEXT,
    last_modified TEXT,
    -- Autres colonnes selon les mu00e9tadonnu00e9es disponibles
);
```

Une table secondaire `sql_presets` stocke les requu00eates SQL personnalisu00e9es :

```sql
CREATE TABLE IF NOT EXISTS sql_presets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    category TEXT,
    query TEXT
);
```
