#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module d'exportation vers différentes bases de données
Auteur: Geoffroy Streit (avec l'aide de Cascade)
"""

import logging
import sqlite3

# Imports conditionnels pour éviter les erreurs si les modules ne sont pas installés
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import psycopg2
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class DBExporter:
    """Classe pour exporter des données vers différentes bases de données"""
    
    def __init__(self):
        """Initialisation du module d'exportation"""
        self.logger = logging.getLogger('mp3tag_analyzer.db_exporter')
    
    def export_to_mysql(self, data, config):
        """Exporte les données vers une base de données MySQL
        
        Args:
            data (list): Liste de dictionnaires contenant les données à exporter
            config (dict): Configuration de connexion MySQL (host, user, password, database, table)
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        if not MYSQL_AVAILABLE:
            raise ImportError("Le module mysql-connector-python n'est pas installé.")
            
        try:
            # Connexion à la base de données MySQL
            conn = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                database=config['database']
            )
            cursor = conn.cursor()
            
            # Création de la table si elle n'existe pas
            self._create_mysql_table(cursor, config['table'], data[0] if data else {})
            
            # Insertion des données
            records_inserted = 0
            for row in data:
                # Filtrer les colonnes qui existent dans la table
                valid_columns = self._get_valid_columns(row, self._get_mysql_table_columns(cursor, config['table']))
                if not valid_columns:
                    continue
                    
                placeholders = ', '.join(['%s'] * len(valid_columns))
                columns = ', '.join(f"`{col}`" for col in valid_columns)
                values = [row.get(col) for col in valid_columns]
                
                query = f"INSERT INTO `{config['table']}` ({columns}) VALUES ({placeholders})"
                cursor.execute(query, values)
                records_inserted += 1
            
            # Validation des changements
            conn.commit()
            conn.close()
            
            self.logger.info(f"{records_inserted} enregistrements exportés vers MySQL")
            return records_inserted
            
        except mysql.connector.Error as err:
            self.logger.error(f"Erreur MySQL: {err}")
            raise Exception(f"Erreur lors de l'exportation vers MySQL: {str(err)}")
    
    def export_to_postgres(self, data, config):
        """Exporte les données vers une base de données PostgreSQL
        
        Args:
            data (list): Liste de dictionnaires contenant les données à exporter
            config (dict): Configuration de connexion PostgreSQL (host, user, password, database, table)
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("Le module psycopg2 n'est pas installé.")
            
        try:
            # Connexion à la base de données PostgreSQL
            conn = psycopg2.connect(
                host=config['host'],
                user=config['user'],
                password=config['password'],
                dbname=config['database']
            )
            cursor = conn.cursor()
            
            # Création de la table si elle n'existe pas
            self._create_postgres_table(cursor, config['table'], data[0] if data else {})
            
            # Insertion des données
            records_inserted = 0
            for row in data:
                # Filtrer les colonnes qui existent dans la table
                valid_columns = self._get_valid_columns(row, self._get_postgres_table_columns(cursor, config['table']))
                if not valid_columns:
                    continue
                    
                placeholders = ', '.join(['%s'] * len(valid_columns))
                columns = ', '.join(f'"{col}"' for col in valid_columns)
                values = [row.get(col) for col in valid_columns]
                
                query = f'INSERT INTO "{config["table"]}" ({columns}) VALUES ({placeholders})'
                cursor.execute(query, values)
                records_inserted += 1
            
            # Validation des changements
            conn.commit()
            conn.close()
            
            self.logger.info(f"{records_inserted} enregistrements exportés vers PostgreSQL")
            return records_inserted
            
        except psycopg2.Error as err:
            self.logger.error(f"Erreur PostgreSQL: {err}")
            raise Exception(f"Erreur lors de l'exportation vers PostgreSQL: {str(err)}")
    
    def export_from_sqlite(self, sqlite_path, export_type, config):
        """Exporte les données depuis SQLite vers un autre type de base de données
        
        Args:
            sqlite_path (str): Chemin vers la base de données SQLite
            export_type (str): Type d'export ('mysql' ou 'postgres')
            config (dict): Configuration de connexion
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        try:
            # Connexion à la base de données SQLite source
            conn = sqlite3.connect(sqlite_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Récupération des données
            cursor.execute("SELECT * FROM mp3_tags")
            rows = cursor.fetchall()
            
            # Conversion des données en liste de dictionnaires
            data = [dict(row) for row in rows]
            conn.close()
            
            # Export vers la base de données cible
            if export_type.lower() == 'mysql':
                return self.export_to_mysql(data, config)
            elif export_type.lower() == 'postgres':
                return self.export_to_postgres(data, config)
            else:
                raise ValueError(f"Type d'export non supporté: {export_type}")
                
        except sqlite3.Error as err:
            self.logger.error(f"Erreur SQLite: {err}")
            raise Exception(f"Erreur lors de la lecture de la base SQLite: {str(err)}")
    
    def _create_mysql_table(self, cursor, table_name, sample_row):
        """Crée une table MySQL si elle n'existe pas"""
        if not sample_row:
            return
            
        # Construction des colonnes en se basant sur les données d'exemple
        columns = []
        for col_name in sample_row.keys():
            # Utiliser des types appropriés en fonction des types de données dans MP3tag
            columns.append(f"`{col_name}` TEXT")
        
        # Ajout d'une colonne ID auto-incrémentée comme clé primaire
        columns_str = ', '.join(columns)
        query = f"""CREATE TABLE IF NOT EXISTS `{table_name}` (
            `id` INT AUTO_INCREMENT PRIMARY KEY,
            {columns_str}
        )"""
        
        cursor.execute(query)
    
    def _create_postgres_table(self, cursor, table_name, sample_row):
        """Crée une table PostgreSQL si elle n'existe pas"""
        if not sample_row:
            return
            
        # Construction des colonnes en se basant sur les données d'exemple
        columns = []
        for col_name in sample_row.keys():
            # Utiliser des types appropriés en fonction des types de données dans MP3tag
            columns.append(f'"{col_name}" TEXT')
        
        # Ajout d'une colonne ID auto-incrémentée comme clé primaire
        columns_str = ', '.join(columns)
        query = f"""CREATE TABLE IF NOT EXISTS "{table_name}" (
            "id" SERIAL PRIMARY KEY,
            {columns_str}
        )"""
        
        cursor.execute(query)
    
    def _get_mysql_table_columns(self, cursor, table_name):
        """Récupère la liste des colonnes d'une table MySQL"""
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        return [row[0] for row in cursor.fetchall()]
    
    def _get_postgres_table_columns(self, cursor, table_name):
        """Récupère la liste des colonnes d'une table PostgreSQL"""
        cursor.execute(f"""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = '{table_name}'
        """)
        return [row[0] for row in cursor.fetchall()]
    
    def _get_valid_columns(self, row, table_columns):
        """Filtre les colonnes qui existent dans la table"""
        return [col for col in row.keys() if col in table_columns]
