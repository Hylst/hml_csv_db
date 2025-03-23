#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module de traitement des fichiers CSV
Auteur: Geoffroy Streit
"""

import csv
import logging
import os
import sys
import io

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(),
                              logging.FileHandler('mp3tag_analyzer.log')])

# Augmenter la limite de taille des champs CSV au maximum possible
try:
    # Essayer d'augmenter la limite au maximum possible sur le système
    max_int = sys.maxsize
    while True:
        try:
            csv.field_size_limit(max_int)
            break
        except OverflowError:
            max_int = int(max_int / 10)
    
    logging.info(f"Limite de taille des champs CSV définie à {max_int}")
except Exception as e:
    logging.error(f"Erreur lors de la définition de la limite de taille des champs CSV: {e}")

class CSVParser:
    """Parseur de fichiers CSV générés par MP3tag"""
    
    def __init__(self):
        self.logger = logging.getLogger('mp3tag_analyzer.csv')
        # Entêtes attendues dans un fichier MP3tag
        self.expected_headers = [
            "Title", "Artist", "Album", "Year", "Genre", "Comment", "ISRC", "Language", 
            "AudioLength", "FileSize", "Crc", "FileCreateDate", "LastModified", "RelativePath", 
            "Filename", "Extension", "Directory", "ParentDirectory", "Keywords", "Mood", 
            "Usage", "Song", "ModeStereo", "BPM", "Codec", "Bitrate", "Samplerate", "VBR", 
            "TagType", "CoverDescription", "CoverSize", "CoverType", "CoverMime", 
            "CoverHeight", "CoverWidth", "UnSyncLyrics", "SrcFix", "PlayCounter"
        ]
    
    def detect_encoding(self, file_path):
        """Détecte l'encodage d'un fichier
        
        Args:
            file_path (str): Chemin du fichier à analyser
            
        Returns:
            str: Encodage détecté ou 'utf-16-le' par défaut
        """
        # Où nous allons chercher le BOM (Byte Order Mark)
        encodings_boms = {
            'utf-8-sig': (0xEF, 0xBB, 0xBF),
            'utf-16-le': (0xFF, 0xFE),
            'utf-16-be': (0xFE, 0xFF),
            'utf-32-le': (0xFF, 0xFE, 0x00, 0x00),
            'utf-32-be': (0x00, 0x00, 0xFE, 0xFF),
        }
        
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(4)  # Lire les 4 premiers octets pour détecter le BOM
                if not raw:
                    self.logger.error(f"Fichier {file_path} vide")
                    return 'utf-8'

                # Vérifier BOM
                for enc, bom in encodings_boms.items():
                    if raw.startswith(bytes(bom)):
                        self.logger.info(f"BOM détecté pour {file_path}: {enc}")
                        return enc
                
                # Si pas de BOM, essayons de détecter l'encodage
                # Vérifier UTF-16-LE sans BOM (cas courant pour MP3tag)
                # Si nous avons des octets nuls alternativement, c'est probablement de l'UTF-16
                if len(raw) >= 2 and (raw[1] == 0 or raw[3] == 0):
                    self.logger.info(f"Encodage probablement UTF-16-LE pour {file_path}")
                    return 'utf-16-le'
                
                # Sinon, c'est probablement UTF-8 ou ANSI
                self.logger.info(f"Encodage déduit pour {file_path}: utf-8")
                return 'utf-8'
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection de l'encodage: {e}")
            # Retour par défaut à UTF-16-LE (encodage courant de MP3tag)
            return 'utf-16-le'
    
    def parse_file(self, file_path):
        """Analyse un fichier CSV
        
        Args:
            file_path (str): Chemin du fichier CSV à analyser
            
        Returns:
            tuple: (entêtes, données)
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Le fichier {file_path} n'existe pas")
            return None, None
        
        # Détection de l'encodage
        encoding = self.detect_encoding(file_path)
        self.logger.info(f"Tentative de lecture avec l'encodage: {encoding}")
        
        try:
            # Méthode directe de lecture CSV avec l'encodage détecté
            with open(file_path, 'r', encoding=encoding, newline='') as csvfile:
                # Essayer de déterminer le séparateur
                sample = csvfile.read(1024)  # Lire un échantillon
                csvfile.seek(0)  # Revenir au début
                
                # Déterminer le séparateur (MP3tag utilise typiquement des points-virgules)
                delimiter = ';'  # Par défaut
                if ';' not in sample and ',' in sample:
                    delimiter = ','
                
                self.logger.info(f"Séparateur détecté: {delimiter}")
                
                # Utiliser le dialect sniffer pour détecter le format CSV
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=delimiter)
                    reader = csv.reader(csvfile, dialect)
                except Exception:
                    # Si le sniffer échoue, utiliser un reader standard
                    reader = csv.reader(csvfile, delimiter=delimiter)
                
                # Lire les entêtes
                try:
                    headers = next(reader)
                    # Traiter les entêtes (supprimer les espaces, les BOM, etc.)
                    headers = [h.strip().replace('\ufeff', '') for h in headers]
                    
                    # Déboguer les entêtes
                    self.logger.info(f"Entêtes brutes: {headers}")
                    for i, h in enumerate(headers):
                        self.logger.info(f"Entête {i}: '{h}', longueur={len(h)}, octets={[ord(c) for c in h]}")
                    
                    # Vérifier la validité des entêtes
                    if not headers or len(headers) <= 1 or not any(h for h in headers if h):
                        self.logger.error(f"Format d'entête invalide: {headers}")
                        return None, None
                except StopIteration:
                    self.logger.error(f"Fichier {file_path} vide ou mal formatté")
                    return None, None
                
                # Lire les données
                data = []
                for row in reader:
                    if not row or all(not cell for cell in row):
                        continue  # Ignorer les lignes vides
                    
                    # Ajuster la taille de la ligne si nécessaire
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    elif len(row) > len(headers):
                        row = row[:len(headers)]
                    
                    # Créer un dictionnaire pour la ligne
                    row_dict = {}
                    for i, h in enumerate(headers):
                        if h:  # Ignorer les entêtes vides
                            row_dict[h] = row[i]
                    
                    if row_dict:  # Ajouter seulement si la ligne a des données
                        data.append(row_dict)
            
            if not data:
                self.logger.error(f"Aucune donnée trouvée dans le fichier {file_path}")
                return None, None
            
            self.logger.info(f"Fichier {file_path} lu avec succès. {len(data)} enregistrements trouvés.")
            return headers, data
        
        except UnicodeDecodeError as e:
            self.logger.error(f"Erreur de décodage avec l'encodage {encoding}: {e}")
            
            # Essayer une méthode alternative avec lecture binaire et décodage manuel
            try:
                self.logger.info("Tentative de lecture alternative...")
                with open(file_path, 'rb') as f:
                    raw_data = f.read()
                
                # Essayer différents encodages
                for alt_encoding in [encoding, 'utf-16-le', 'utf-16-be', 'utf-8', 'windows-1252']:
                    try:
                        text = raw_data.decode(alt_encoding.replace('-sig', ''), errors='replace')
                        lines = text.splitlines()
                        
                        if not lines:
                            continue
                        
                        # Traiter la première ligne (entêtes)
                        header_line = lines[0].strip().replace('\ufeff', '')
                        
                        # Déterminer le séparateur
                        delimiter = ';'  # MP3tag utilise typiquement des points-virgules
                        if ';' not in header_line and ',' in header_line:
                            delimiter = ','
                        
                        headers = [h.strip() for h in header_line.split(delimiter)]
                        
                        # Vérifier que les entêtes sont valides
                        if len(headers) <= 1 or not any(h for h in headers if h):
                            continue
                        
                        # Traiter les lignes de données
                        data = []
                        for line in lines[1:]:
                            if not line.strip():
                                continue
                            
                            fields = self._split_csv_line(line.strip(), delimiter)
                            
                            # Ajuster la taille de la ligne si nécessaire
                            if len(fields) < len(headers):
                                fields.extend([''] * (len(headers) - len(fields)))
                            elif len(fields) > len(headers):
                                fields = fields[:len(headers)]
                            
                            # Créer un dictionnaire pour la ligne
                            row_dict = {}
                            for i, h in enumerate(headers):
                                if h:  # Ignorer les entêtes vides
                                    row_dict[h] = fields[i]
                            
                            if row_dict:  # Ajouter seulement si la ligne a des données
                                data.append(row_dict)
                        
                        if data:  # Si des données ont été lues
                            self.logger.info(f"Fichier {file_path} lu avec succès via la méthode alternative. {len(data)} enregistrements.")
                            return headers, data
                    except UnicodeDecodeError:
                        continue
            except Exception as e:
                self.logger.error(f"Erreur lors de la lecture alternative: {e}")
        
        except Exception as e:
            self.logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
        
        # Dernière tentative: utiliser directement le module csv avec les entêtes connues
        try:
            self.logger.info("Dernière tentative avec les entêtes connues...")
            with open(file_path, 'r', encoding='utf-16-le', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=';')
                headers = self.expected_headers  # Utiliser les entêtes prédéfinies
                
                # Sauter la ligne d'entête
                next(reader, None)
                
                data = []
                for row in reader:
                    if not row or all(not cell for cell in row):
                        continue
                    
                    # Ajuster la taille
                    if len(row) < len(headers):
                        row.extend([''] * (len(headers) - len(row)))
                    elif len(row) > len(headers):
                        row = row[:len(headers)]
                    
                    # Créer un dictionnaire
                    row_dict = dict(zip(headers, row))
                    data.append(row_dict)
                
                if data:
                    self.logger.info(f"Fichier {file_path} lu avec succès via les entêtes prédéfinies. {len(data)} enregistrements.")
                    return headers, data
        except Exception as e:
            self.logger.error(f"Erreur lors de la dernière tentative: {e}")
        
        self.logger.error(f"Impossible de lire le fichier {file_path} avec aucune méthode")
        return None, None
    
    def _split_csv_line(self, line, delimiter):
        """Divise une ligne CSV en respectant les guillemets
        
        Args:
            line (str): Ligne CSV à diviser
            delimiter (str): Séparateur à utiliser
            
        Returns:
            list: Liste des champs
        """
        fields = []
        current_field = ""
        in_quotes = False
        
        for char in line:
            if char == '"':
                in_quotes = not in_quotes
                current_field += char
            elif char == delimiter and not in_quotes:
                # Enlever les guillemets entourant le champ si nécessaire
                if current_field.startswith('"') and current_field.endswith('"') and len(current_field) > 1:
                    current_field = current_field[1:-1]
                fields.append(current_field)
                current_field = ""
            else:
                current_field += char
        
        # Ajouter le dernier champ
        if current_field.startswith('"') and current_field.endswith('"') and len(current_field) > 1:
            current_field = current_field[1:-1]
        fields.append(current_field)
        
        return fields
    
    def export_to_csv(self, data, headers, output_path, encoding='utf-16-le'):
        """Exportation des données vers un fichier CSV
        
        Args:
            data (list): Données à exporter
            headers (list): Entêtes des colonnes
            output_path (str): Chemin du fichier de sortie
            encoding (str): Encodage à utiliser
            
        Returns:
            bool: True si l'exportation est réussie, False sinon
        """
        try:
            with open(output_path, 'w', encoding=encoding, newline='') as file:
                writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_MINIMAL)
                
                # Écrire l'entête
                writer.writerow(headers)
                # Écrire les données
                for row in data:
                    # Extraire les valeurs dans l'ordre des entêtes
                    values = [row.get(h, '') for h in headers]
                    writer.writerow(values)
                
                self.logger.info(f"Données exportées avec succès vers {output_path}")
                return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exportation des données: {e}")
            return False
