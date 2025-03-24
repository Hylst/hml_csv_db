#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module de gestion de la base de données
Auteur: Geoffroy Streit
"""

import sqlite3
import os
import datetime
import logging

class DatabaseManager:
    """Gestionnaire de base de données SQLite pour stocker les données MP3"""
    
    def __init__(self, db_path=None):
        """Initialisation du gestionnaire de base de données
        
        Args:
            db_path (str, optional): Chemin vers la base de données. Si None, une base temporaire en mémoire est créée.
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.logger = logging.getLogger('mp3tag_analyzer.db')
        
        # Mapping entre les noms de colonnes du CSV et ceux de la base de données
        self.column_mapping = {
            # Noms standards MP3tag -> Noms dans la base de données
            'Title': 'title',
            'Artist': 'artist',
            'Album': 'album',
            'Year': 'year',
            'Genre': 'genre',
            'Comment': 'comment',
            'ISRC': 'isrc',
            'Language': 'language',
            'AudioLength': 'audio_length',
            'FileSize': 'file_size',
            'Crc': 'crc',
            'FileCreateDate': 'file_create_date',
            'LastModified': 'last_modified',
            'RelativePath': 'relative_path',
            'Filename': 'filename',
            'Extension': 'extension',
            'Directory': 'directory',
            'ParentDirectory': 'parent_directory',
            'Keywords': 'keywords',
            'Mood': 'mood',
            'Usage': 'usage',
            'Song': 'song',
            'ModeStereo': 'mode_stereo',
            'BPM': 'bpm',
            'Codec': 'codec',
            'Bitrate': 'bitrate',
            'Samplerate': 'samplerate',
            'VBR': 'vbr',
            'TagType': 'tag_type',
            'CoverDescription': 'cover_description',
            'CoverSize': 'cover_size',
            'CoverType': 'cover_type',
            'CoverMime': 'cover_mime',
            'CoverHeight': 'cover_height',
            'CoverWidth': 'cover_width',
            'UnSyncLyrics': 'unsynced_lyrics',
            'SrcFix': 'src_fix',
            'PlayCounter': 'play_counter'
        }
    
    def connect(self, db_path=None):
        """Connexion à la base de données
        
        Args:
            db_path (str, optional): Chemin vers la base de données. Remplace le chemin défini à l'initialisation.
            
        Returns:
            bool: True si la connexion est réussie, False sinon
        """
        if db_path:
            self.db_path = db_path
            
        try:
            if self.db_path:
                self.conn = sqlite3.connect(self.db_path)
            else:
                self.conn = sqlite3.connect(':memory:')
            
            self.cursor = self.conn.cursor()
            self.logger.info(f"Connexion à la base de données réussie: {self.db_path}")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erreur de connexion à la base de données: {e}")
            return False
    
    def close(self):
        """Fermeture de la connexion à la base de données"""
        if self.conn:
            self.conn.close()
            self.logger.info("Connexion à la base de données fermée")
    
    def create_tables(self):
        """Création des tables dans la base de données"""
        try:
            # Création de la table mp3_files avec une clé primaire unique
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mp3_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relative_path TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    title TEXT,
                    artist TEXT,
                    album TEXT,
                    year INTEGER,
                    genre TEXT,
                    comment TEXT,
                    isrc TEXT,
                    language TEXT,
                    audio_length INTEGER,
                    file_size TEXT,
                    crc TEXT,
                    file_create_date TEXT,
                    last_modified TEXT,
                    extension TEXT,
                    directory TEXT,
                    parent_directory TEXT,
                    keywords TEXT,
                    mood TEXT,
                    usage TEXT,
                    song TEXT,
                    mode_stereo TEXT,
                    bpm INTEGER,
                    codec TEXT,
                    bitrate TEXT,
                    samplerate TEXT,
                    vbr TEXT,
                    tag_type TEXT,
                    cover_description TEXT,
                    cover_size TEXT,
                    cover_type TEXT,
                    cover_mime TEXT,
                    cover_height INTEGER,
                    cover_width INTEGER,
                    unsync_lyrics TEXT,
                    src_fix TEXT,
                    play_counter INTEGER,
                    import_date TEXT,
                    UNIQUE(relative_path, filename)  -- Clé unique pour éviter les duplications
                )
            ''')
            
            self.logger.info("Tables créées avec succès")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de la création des tables: {e}")
            return False
    
    def insert_mp3_data(self, mp3_data):
        """Insertion des données MP3 dans la base de données
        
        Args:
            mp3_data (list): Liste de dictionnaires contenant les données MP3
            
        Returns:
            bool: True si l'insertion est réussie, False sinon
        """
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            inserted_count = 0
            
            for row in mp3_data:
                # Ajouter la date d'importation
                mapped_row = {'import_date': now}
                
                # Mapper les colonnes du CSV vers les colonnes de la base de données
                for csv_col, value in row.items():
                    # Obtenir le nom de colonne dans la base de données
                    if csv_col in self.column_mapping:
                        db_col = self.column_mapping[csv_col]
                        mapped_row[db_col] = value
                    else:
                        # Convertir automatiquement (fallback)
                        db_col = csv_col.lower().replace(' ', '_')
                        mapped_row[db_col] = value
                
                # Préparer les colonnes et valeurs
                columns = ', '.join(mapped_row.keys())
                placeholders = ', '.join(['?' for _ in mapped_row.keys()])
                
                # Préparer la requête
                query = f"INSERT INTO mp3_files ({columns}) VALUES ({placeholders})"
                
                # Exécuter la requête
                self.cursor.execute(query, list(mapped_row.values()))
                inserted_count += 1
            
            self.conn.commit()
            self.logger.info(f"{inserted_count} enregistrements insérés avec succès")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de l'insertion des données: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.conn.rollback()
            return False
    
    def insert_records(self, mp3_data):
        """Insertion des données MP3 dans la base de données
        
        Args:
            mp3_data (list): Liste de dictionnaires contenant les données MP3
            
        Returns:
            int: Nombre d'enregistrements insérés
        """
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            inserted_count = 0
            duplicates_count = 0
            
            # S'assurer que les tables existent
            self.create_tables()
            
            for row in mp3_data:
                # Ajouter la date d'importation
                mapped_row = {'import_date': now}
                
                # Méthode plus flexible pour traiter n'importe quelle structure de fichier CSV
                # 1. Extraire toutes les colonnes disponibles dans la donnée CSV
                for csv_col, value in row.items():
                    # Obtenir le nom de colonne normalisé pour la base de données
                    if csv_col in self.column_mapping:
                        db_col = self.column_mapping[csv_col]
                    else:
                        # Normaliser automatiquement le nom (fallback)
                        db_col = csv_col.lower().replace(' ', '_')
                    
                    # Stocker la valeur avec le nom de colonne normalisé
                    mapped_row[db_col] = value
                
                # Normaliser le chemin relatif et le nom de fichier
                if 'relative_path' in mapped_row:
                    mapped_row['relative_path'] = os.path.normpath(mapped_row['relative_path'].strip())
                if 'filename' in mapped_row:
                    mapped_row['filename'] = mapped_row['filename'].strip()
                
                # 2. Vérifier quelles colonnes existent dans la table mp3_files
                # Récupérer la structure de la table
                self.cursor.execute("PRAGMA table_info(mp3_files)")
                table_columns = [info[1] for info in self.cursor.fetchall()]
                
                # 3. Ne conserver que les colonnes qui existent dans la table
                valid_columns = {}
                for col, val in mapped_row.items():
                    if col in table_columns:
                        valid_columns[col] = val
                
                # Si aucune colonne valide, passer à l'enregistrement suivant
                if not valid_columns:
                    self.logger.warning(f"Enregistrement ignoré car aucune colonne valide: {row}")
                    continue
                
                # Vérifier si l'enregistrement existe déjà
                existing_query = "SELECT COUNT(*) FROM mp3_files WHERE relative_path = ? AND filename = ?"
                self.cursor.execute(existing_query, (valid_columns.get('relative_path', ''), valid_columns.get('filename', '')))
                count = self.cursor.fetchone()[0]
                
                if count > 0:
                    self.logger.info(f"Enregistrement déjà existant: {valid_columns.get('relative_path', '')}/{valid_columns.get('filename', '')}")
                    duplicates_count += 1
                    continue
                
                # Préparer la requête avec seulement les colonnes valides
                columns = ', '.join(valid_columns.keys())
                placeholders = ', '.join(['?' for _ in valid_columns.keys()])
                
                # Préparer la requête
                query = f"INSERT INTO mp3_files ({columns}) VALUES ({placeholders})"
                
                # Exécuter la requête
                try:
                    self.cursor.execute(query, list(valid_columns.values()))
                    inserted_count += 1
                except sqlite3.Error as e:
                    self.logger.error(f"Erreur lors de l'insertion de l'enregistrement: {e}")
                    self.logger.error(f"Requête: {query}")
                    self.logger.error(f"Valeurs: {list(valid_columns.values())}")
                    # Continuer avec les autres enregistrements
                    continue
            
            # Valider toutes les insertions
            self.conn.commit()
            self.logger.info(f"Import terminé: {inserted_count} insérés, {duplicates_count} ignorés (doublons)")
            return inserted_count
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de l'insertion des données: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            self.conn.rollback()
            return 0
    
    def get_all_records(self):
        """Récupération de tous les enregistrements
        
        Returns:
            list: Liste de dictionnaires contenant les données MP3
        """
        try:
            self.cursor.execute("SELECT * FROM mp3_files")
            columns = [column[0] for column in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de la récupération des données: {e}")
            return []
    
    def search_records(self, criteria):
        """Recherche d'enregistrements selon des critères
        
        Args:
            criteria (dict): Dictionnaire des critères de recherche
            
        Returns:
            list: Liste de dictionnaires contenant les données MP3 correspondant aux critères
        """
        try:
            conditions = []
            values = []
            
            for key, value in criteria.items():
                if value:
                    conditions.append(f"{key} LIKE ?")
                    values.append(f"%{value}%")
            
            if not conditions:
                return self.get_all_records()
            
            query = f"SELECT * FROM mp3_files WHERE {' AND '.join(conditions)}"
            self.cursor.execute(query, values)
            
            columns = [column[0] for column in self.cursor.description]
            results = []
            
            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de la recherche: {e}")
            return []
    
    def delete_record(self, record_id):
        """Suppression d'un enregistrement
        
        Args:
            record_id (int): ID de l'enregistrement à supprimer
            
        Returns:
            bool: True si la suppression est réussie, False sinon
        """
        try:
            self.cursor.execute("DELETE FROM mp3_files WHERE id = ?", (record_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors de la suppression: {e}")
            self.conn.rollback()
            return False
    
    def clear_table(self):
        """Suppression de tous les enregistrements de la table
        
        Returns:
            bool: True si la suppression est réussie, False sinon
        """
        try:
            self.cursor.execute("DELETE FROM mp3_files")
            self.conn.commit()
            self.logger.info("Table vidée avec succès")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Erreur lors du vidage de la table: {e}")
            self.conn.rollback()
            return False
    
    def save_database(self, db_path, data):
        """Sauvegarde des données dans une nouvelle base de données
        
        Args:
            db_path (str): Chemin de la base de données à créer
            data (list): Données à enregistrer
            
        Returns:
            str: Chemin de la base de données si succès, None sinon
        """
        try:
            # Fermeture de la connexion actuelle si elle existe
            if self.conn:
                self.close()
            
            # Création de la nouvelle base de données
            if self.connect(db_path) and self.create_tables():
                # Insertion des données
                if self.insert_mp3_data(data):
                    self.logger.info(f"Base de données enregistrée avec succès dans {db_path}")
                    return db_path
                else:
                    self.logger.error("Erreur lors de l'insertion des données")
            else:
                self.logger.error(f"Impossible de créer la base de données {db_path}")
            
            return None
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde de la base de données: {e}")
            return None
