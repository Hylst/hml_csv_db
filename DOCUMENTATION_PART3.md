# Documentation MP3Tag Analyzer - Partie 3

## Export vers bases externes

### Export vers MySQL

L'application permet d'exporter les donnu00e9es vers une base MySQL :

#### Configuration requise

- Serveur MySQL accessible
- Module `mysql-connector-python` installu00e9
- Droits suffisants pour cru00e9er des tables et insu00e9rer des donnu00e9es

#### Processus d'export

1. Accu00e9dez u00e0 Fichier > Exporter vers... > MySQL
2. Configurez les paramu00e8tres de connexion :
   - Hu00f4te (par du00e9faut : localhost)
   - Port (par du00e9faut : 3306)
   - Utilisateur et mot de passe
   - Nom de la base de donnu00e9es
   - Nom de la table (par du00e9faut : mp3_tags)
3. Cliquez sur OK pour lancer l'export

L'application cru00e9era automatiquement la table si elle n'existe pas, avec un schu00e9ma adaptu00e9 aux donnu00e9es actuelles.

#### Mapping des types de donnu00e9es

Lors de l'export vers MySQL, les types de donnu00e9es sont mappu00e9s comme suit :
- Champs textuels : VARCHAR(255) ou TEXT pour les champs longs
- Champs numu00e9riques : INT ou FLOAT selon le contenu
- Dates : DATETIME

### Export vers PostgreSQL

L'application permet u00e9galement d'exporter les donnu00e9es vers PostgreSQL :

#### Configuration requise

- Serveur PostgreSQL accessible
- Module `psycopg2-binary` installu00e9
- Droits suffisants pour cru00e9er des tables et insu00e9rer des donnu00e9es

#### Processus d'export

1. Accu00e9dez u00e0 Fichier > Exporter vers... > PostgreSQL
2. Configurez les paramu00e8tres de connexion :
   - Hu00f4te (par du00e9faut : localhost)
   - Port (par du00e9faut : 5432)
   - Utilisateur et mot de passe
   - Nom de la base de donnu00e9es
   - Nom de la table (par du00e9faut : mp3_tags)
3. Cliquez sur OK pour lancer l'export

Comme pour MySQL, l'application cru00e9era automatiquement la table si nu00e9cessaire.

#### Mapping des types de donnu00e9es

Lors de l'export vers PostgreSQL, les types de donnu00e9es sont mappu00e9s comme suit :
- Champs textuels : VARCHAR(255) ou TEXT
- Champs numu00e9riques : INTEGER ou REAL
- Dates : TIMESTAMP

### Limites et considu00e9rations

- L'export est unidirectionnel (de l'application vers la base externe)
- Les modifications ultu00e9rieures dans la base externe ne seront pas synchronisu00e9es
- Pour les collections volumineuses, l'export peut prendre du temps
- Les contraintes et index ne sont pas cru00e9u00e9s automatiquement

## Bonnes pratiques

### Gestion des fichiers CSV

- **Export depuis MP3Tag** :
  - Exportez toutes les colonnes pertinentes
  - Utilisez l'encodage UTF-16-LE (par du00e9faut)
  - Utilisez le su00e9parateur point-virgule (;)
- **Taille des fichiers** :
  - Pour les grandes collections, divisez l'export en plusieurs fichiers
  - Importez-les su00e9quentiellement dans l'application

### Optimisation des performances

- **Chargement de donnu00e9es** :
  - Privilu00e9giez le chargement depuis une base SQLite plutu00f4t que CSV pour les utilisations ru00e9pu00e9tu00e9es
  - Sauvegardez ru00e9guliu00e8rement votre base de donnu00e9es
- **Requu00eates SQL** :
  - Utilisez des clauses WHERE spu00e9cifiques pour limiter les ru00e9sultats
  - Ajoutez LIMIT pour les requu00eates exploratoires
  - u00c9vitez les jointures complexes sur de grandes tables

### Su00e9curitu00e9 des donnu00e9es

- **Bases de donnu00e9es externes** :
  - Utilisez un utilisateur avec des privilu00e8ges limitu00e9s
  - Ne stockez pas les mots de passe dans l'application
  - Utilisez des connexions su00e9curisu00e9es si possible (SSL)
- **Sauvegarde** :
  - Effectuez des sauvegardes ru00e9guliu00e8res de vos bases de donnu00e9es
  - Conservez plusieurs versions de sauvegarde

## Du00e9pannage

### Problu00e8mes d'importation CSV

| Problu00e8me | Cause possible | Solution |
|-----------|----------------|----------|
| Caractu00e8res incorrects | Encodage non du00e9tectu00e9 | Vu00e9rifiez l'encodage dans MP3Tag |
| Colonnes manquantes | Structure CSV non standard | Vu00e9rifiez les paramu00e8tres d'export |
| Import lent | Fichier volumineux | Divisez en fichiers plus petits |
| Application figu00e9e | Problu00e8me de mu00e9moire | Redu00e9marrez l'application |

### Problu00e8mes de base de donnu00e9es

| Problu00e8me | Cause possible | Solution |
|-----------|----------------|----------|
| Erreur SQLite | Base de donnu00e9es corrompue | Utilisez une sauvegarde antu00e9rieure |
| Erreur de connexion MySQL | Serveur inaccessible | Vu00e9rifiez les paramu00e8tres ru00e9seau |
| Erreur de connexion PostgreSQL | Authentification u00e9chouu00e9e | Vu00e9rifiez les identifiants |
| Table non cru00e9u00e9e | Privilu00e8ges insuffisants | Vu00e9rifiez les droits utilisateur |

### Problu00e8mes d'interface

| Problu00e8me | Cause possible | Solution |
|-----------|----------------|----------|
| Interface non ru00e9active | Opu00e9ration longue en cours | Attendez la fin de l'opu00e9ration |
| Colonnes mal affichu00e9es | Redimensionnement incorrect | Ajustez manuellement les largeurs |
| Requu00eate SQL sans ru00e9sultat | Erreur de syntaxe | Vu00e9rifiez la syntaxe de la requu00eate |

### Journaux d'erreurs

L'application gu00e9nu00e8re des journaux d'erreurs dans le fichier `mp3tag_analyzer.log`. Consultez ce fichier en cas de problu00e8me pour obtenir des informations du00e9taillu00e9es sur les erreurs rencontru00e9es.
