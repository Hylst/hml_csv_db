# Aide de MP3Tag Analyzer

## Présentation générale

MP3Tag Analyzer est une application qui permet d'analyser, rechercher et filtrer les métadonnées de vos fichiers MP3 exportées depuis le logiciel MP3Tag. Cette application offre une interface graphique conviviale pour explorer vos collections de musique et obtenir des statistiques détaillées.

## Interface utilisateur

L'interface de MP3Tag Analyzer est organisée en plusieurs sections :

### Barre de menu

- **Fichier** : Contient les options pour charger/enregistrer des données et exporter vers différentes bases de données
  - *Charger CSV* : Importe un fichier CSV généré par MP3Tag
  - *Charger Base de Données* : Ouvre une base de données SQLite existante
  - *Enregistrer Base de Données* : Sauvegarde les données actuelles dans un fichier SQLite
  - *Exporter vers...* : Sous-menu pour exporter vers MySQL ou PostgreSQL
  - *Quitter* : Ferme l'application

- **Édition** : Options d'édition et de manipulation des données

- **Aide** : Accès à l'aide et aux informations sur l'application
  - *À propos* : Affiche les informations sur la version et l'auteur

### Barre d'outils principale

- **Charger CSV** : Bouton pour importer un fichier CSV
- **Charger Base de Données** : Bouton pour ouvrir une base SQLite
- **Enregistrer Base de Données** : Bouton pour sauvegarder en SQLite

### Zone de recherche

- **Champ de recherche** : Saisissez votre terme de recherche
- **Colonne** : Sélectionnez la colonne dans laquelle rechercher (ou "Tous les champs")
- **Bouton Rechercher** : Lance la recherche

### Onglets

- **Données** : Affiche les données sous forme de tableau
- **Requêtes SQL** : Interface pour exécuter des requêtes SQL personnalisées

## Fonctionnalités détaillées

### Importation de fichiers CSV

L'application est conçue pour traiter les fichiers CSV générés par MP3Tag. Elle prend en charge :

- Les fichiers encodés en UTF-16-LE (format standard de MP3Tag) et UTF-8
- Les séparateurs point-virgule (;) et virgule (,)
- Différentes structures de colonnes (ordre variable, noms différents)

Pour importer un fichier CSV :
1. Cliquez sur "Charger CSV" dans la barre d'outils ou le menu Fichier
2. Sélectionnez votre fichier CSV généré par MP3Tag
3. L'application détectera automatiquement l'encodage et le séparateur
4. Les données seront chargées dans le tableau et insérées dans une base de données temporaire

### Recherche

La fonction de recherche permet de filtrer les données selon différents critères :

1. Saisissez votre terme de recherche dans le champ prévu
2. Sélectionnez la colonne dans laquelle rechercher (ou "Tous les champs")
3. Cliquez sur "Rechercher" ou appuyez sur Entrée
4. Les résultats s'affichent dans le tableau

### Tri des données

Vous pouvez trier les données en cliquant sur l'en-tête de la colonne souhaitée :
- Premier clic : tri croissant
- Second clic : tri décroissant
- Troisième clic : retour à l'ordre initial

### Requêtes SQL

L'onglet "Requêtes SQL" permet d'exécuter des requêtes SQL personnalisées sur vos données :

1. Sélectionnez une catégorie dans la liste déroulante
2. Choisissez un preset existant ou écrivez votre propre requête
3. Cliquez sur "Exécuter"
4. Les résultats s'affichent dans l'onglet "Données"

#### Présets disponibles

L'application propose plusieurs présets organisés par catégories :
- **Requêtes générales** : Statistiques globales sur la collection
- **Analyse par artiste** : Statistiques regroupées par artiste
- **Analyse par album** : Statistiques regroupées par album
- **Durée et taille** : Analyse des durées et tailles de fichiers
- **Métadonnées** : Analyse des métadonnées disponibles
- **Formats audio** : Statistiques sur les formats audio
- **Dates** : Analyse chronologique

#### Création de présets personnalisés

Vous pouvez créer et sauvegarder vos propres requêtes SQL :
1. Écrivez votre requête dans le champ de texte
2. Cliquez sur "Sauvegarder"
3. Donnez un nom à votre requête et sélectionnez une catégorie
4. Votre requête sera disponible dans la liste des présets

### Export vers des bases de données externes

L'application permet d'exporter vos données vers MySQL et PostgreSQL :

1. Chargez d'abord un fichier CSV ou une base de données SQLite
2. Dans le menu Fichier, allez dans "Exporter vers..." et choisissez MySQL ou PostgreSQL
3. Configurez les paramètres de connexion dans la boîte de dialogue :
   - Hôte (par défaut : localhost)
   - Port (MySQL : 3306, PostgreSQL : 5432)
   - Utilisateur et mot de passe
   - Nom de la base de données et de la table
4. Cliquez sur OK pour lancer l'exportation

## Astuces et bonnes pratiques

- **Performances** : Pour les grandes collections (>10 000 morceaux), privilégiez l'utilisation de bases de données SQLite plutôt que de recharger le CSV à chaque fois
- **Requêtes SQL** : Utilisez la clause LIMIT pour limiter le nombre de résultats lors de requêtes exploratoires
- **Sauvegarde** : Exportez régulièrement votre base de données pour éviter la perte de données
- **Encodage** : Si vous rencontrez des problèmes d'encodage, vérifiez les paramètres d'export dans MP3Tag

## Résolution des problèmes courants

### Problèmes d'importation CSV

- **Erreur d'encodage** : Vérifiez que votre fichier est bien encodé en UTF-16-LE ou UTF-8
- **Colonnes manquantes** : L'application gère automatiquement les colonnes manquantes, mais certaines fonctionnalités peuvent être limitées
- **Fichier volumineux** : Pour les fichiers très volumineux, l'importation peut prendre du temps

### Problèmes de base de données

- **Erreur de connexion MySQL/PostgreSQL** : Vérifiez vos paramètres de connexion et que le serveur est bien en cours d'exécution
- **Droits insuffisants** : Assurez-vous que l'utilisateur a les droits de création de tables et d'insertion

### Problèmes d'interface

- **Interface figée** : Les opérations longues sont exécutées en arrière-plan, mais peuvent ralentir l'interface
- **Affichage incorrect** : Redimensionnez la fenêtre ou redémarrez l'application

## Informations techniques

- **Structure de la base de données** : Les données sont stockées dans une table `mp3_tags` avec des colonnes correspondant aux métadonnées MP3
- **Requêtes SQL** : L'application utilise SQLite en interne, qui a quelques différences syntaxiques avec MySQL/PostgreSQL
- **Limitations** : Certaines fonctions avancées de SQL peuvent ne pas être disponibles selon le moteur de base de données utilisé
