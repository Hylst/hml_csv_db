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
        # Entêtes possibles dans un fichier MP3tag (liste non exhaustive)
        # Cette liste sert à la validation mais n'est plus obligatoire
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
        
        # Méthode directe de lecture CSV avec l'encodage détecté
        try:
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
                    
                    # Vérifier la validité des entêtes (au moins une entête valide)
                    valid_headers = [h for h in headers if h.strip()]
                    if not valid_headers:
                        self.logger.error(f"Format d'entête invalide: {headers}")
                        return None, None
                    
                    # Supprimer les entêtes vides ou dupliquées
                    clean_headers = []
                    seen = set()
                    for i, h in enumerate(headers):
                        if not h.strip(): 
                            # Remplacer les entêtes vides par un nom générique
                            h = f"Column_{i}"
                        # Gérer les doublons
                        if h in seen:
                            j = 1
                            while f"{h}_{j}" in seen:
                                j += 1
                            h = f"{h}_{j}"
                        seen.add(h)
                        clean_headers.append(h)
                    
                    headers = clean_headers
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
            
            # Essayer avec d'autres encodages en cas d'échec
            for alt_encoding in ['utf-16-le', 'utf-16-be', 'utf-8', 'windows-1252', 'iso-8859-1']:
                if alt_encoding != encoding:
                    try:
                        self.logger.info(f"Tentative avec l'encodage alternatif: {alt_encoding}")
                        with open(file_path, 'r', encoding=alt_encoding, newline='') as csvfile:
                            # Même traitement que ci-dessus
                            sample = csvfile.read(1024)  
                            csvfile.seek(0)  
                            delimiter = ';'  
                            if ';' not in sample and ',' in sample:
                                delimiter = ','
                            self.logger.info(f"Séparateur détecté: {delimiter}")
                            try:
                                dialect = csv.Sniffer().sniff(sample, delimiters=delimiter)
                                reader = csv.reader(csvfile, dialect)
                            except Exception:
                                reader = csv.reader(csvfile, delimiter=delimiter)
                            headers = next(reader)
                            headers = [h.strip().replace('\ufeff', '') for h in headers]
                            self.logger.info(f"Entêtes brutes: {headers}")
                            valid_headers = [h for h in headers if h.strip()]
                            if not valid_headers:
                                self.logger.error(f"Format d'entête invalide: {headers}")
                                return None, None
                            clean_headers = []
                            seen = set()
                            for i, h in enumerate(headers):
                                if not h.strip(): 
                                    h = f"Column_{i}"
                                if h in seen:
                                    j = 1
                                    while f"{h}_{j}" in seen:
                                        j += 1
                                    h = f"{h}_{j}"
                                seen.add(h)
                                clean_headers.append(h)
                            headers = clean_headers
                            data = []
                            for row in reader:
                                if not row or all(not cell for cell in row):
                                    continue  
                                if len(row) < len(headers):
                                    row.extend([''] * (len(headers) - len(row)))
                                elif len(row) > len(headers):
                                    row = row[:len(headers)]
                                row_dict = {}
                                for i, h in enumerate(headers):
                                    row_dict[h] = row[i]
                                if row_dict:  
                                    data.append(row_dict)
                            if data:  
                                self.logger.info(f"Fichier {file_path} lu avec succès via l'encodage alternatif. {len(data)} enregistrements.")
                                return headers, data
                    except UnicodeDecodeError:
                        continue
            
            self.logger.error(f"Impossible de lire le fichier {file_path} avec les encodages disponibles")
            return None, None
        
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse du fichier {file_path}: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
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
                if current_field.startswith('"') and current_field.endswith('"') and len(current_field) > 1:
                    current_field = current_field[1:-1]
                fields.append(current_field)
                current_field = ""
            else:
                current_field += char
        
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
                
                writer.writerow(headers)
                for row in data:
                    values = [row.get(h, '') for h in headers]
                    writer.writerow(values)
                
                self.logger.info(f"Données exportées avec succès vers {output_path}")
                return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exportation des données: {e}")
            return False
