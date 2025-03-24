#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module d'export vers différents formats (CSV, JSON, XML) pour MP3Tag Analyzer
Auteur: Geoffroy Streit
"""

import csv
import json
import xml.dom.minidom as minidom
import xml.etree.ElementTree as ET
import logging
import os
from typing import List, Dict, Any, Optional, Union, Tuple

class FormatExporter:
    """
    Classe pour exporter les données vers différents formats (CSV, JSON, XML)
    """
    
    def __init__(self):
        """
        Initialisation du module d'export
        """
        self.logger = logging.getLogger('mp3tag_analyzer.format_exporter')
    
    def export_to_csv(self, data: List[Dict[str, Any]], file_path: str, 
                      delimiter: str = ';', encoding: str = 'utf-8-sig',
                      include_headers: bool = True) -> int:
        """
        Exporte les données vers un fichier CSV
        
        Args:
            data: Liste de dictionnaires contenant les données à exporter
            file_path: Chemin du fichier CSV de destination
            delimiter: Séparateur de champs (par défaut: point-virgule)
            encoding: Encodage du fichier (par défaut: UTF-8 avec BOM)
            include_headers: Inclure les en-têtes dans le fichier
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        try:
            if not data:
                self.logger.warning("Aucune donnée à exporter vers CSV")
                return 0
            
            # Créer une copie profonde des données pour éviter de les altérer
            data_copy = []
            for item in data:
                # Convertir les valeurs en types Python standards
                item_copy = {}
                for key, value in item.items():
                    # Conversion des types spéciaux si nécessaire
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='replace')
                    item_copy[key] = value
                data_copy.append(item_copy)
            
            # Récupérer les en-têtes (toutes les clés uniques de tous les dictionnaires)
            headers = set()
            for item in data_copy:
                headers.update(item.keys())
            headers = sorted(list(headers))
            
            # Écrire dans le fichier CSV
            with open(file_path, 'w', newline='', encoding=encoding) as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=delimiter, extrasaction='ignore')
                
                if include_headers:
                    writer.writeheader()
                
                writer.writerows(data_copy)
            
            self.logger.info(f"{len(data_copy)} enregistrements exportés vers {file_path}")
            return len(data_copy)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export CSV: {str(e)}")
            raise
    
    def export_to_json(self, data: List[Dict[str, Any]], file_path: str, 
                       encoding: str = 'utf-8', indent: int = 2,
                       as_array: bool = True) -> int:
        """
        Exporte les données vers un fichier JSON
        
        Args:
            data: Liste de dictionnaires contenant les données à exporter
            file_path: Chemin du fichier JSON de destination
            encoding: Encodage du fichier (par défaut: UTF-8)
            indent: Indentation du JSON (par défaut: 2 espaces)
            as_array: Si True, exporte les données comme un tableau JSON;
                     sinon, comme un objet JSON avec des IDs comme clés
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        try:
            if not data:
                self.logger.warning("Aucune donnée à exporter vers JSON")
                return 0
            
            # Créer une copie profonde des données pour éviter de les altérer
            data_copy = []
            for item in data:
                # Convertir les valeurs en types Python standards
                item_copy = {}
                for key, value in item.items():
                    # Conversion des types spéciaux si nécessaire
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='replace')
                    item_copy[key] = value
                data_copy.append(item_copy)
            
            # Préparer les données selon le format demandé
            if as_array:
                json_data = data_copy
            else:
                # Créer un objet avec des IDs comme clés
                json_data = {}
                for i, item in enumerate(data_copy):
                    json_data[f"item_{i}"] = item
            
            # Écrire dans le fichier JSON
            with open(file_path, 'w', encoding=encoding) as f:
                json.dump(json_data, f, indent=indent, ensure_ascii=False)
            
            self.logger.info(f"{len(data_copy)} enregistrements exportés vers {file_path}")
            return len(data_copy)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export JSON: {str(e)}")
            raise
    
    def export_to_xml(self, data: List[Dict[str, Any]], file_path: str, 
                      root_element: str = 'mp3collection', item_element: str = 'track',
                      encoding: str = 'utf-8', pretty_print: bool = True) -> int:
        """
        Exporte les données vers un fichier XML
        
        Args:
            data: Liste de dictionnaires contenant les données à exporter
            file_path: Chemin du fichier XML de destination
            root_element: Nom de l'élément racine (par défaut: 'mp3collection')
            item_element: Nom de l'élément pour chaque piste (par défaut: 'track')
            encoding: Encodage du fichier (par défaut: UTF-8)
            pretty_print: Formater le XML pour la lisibilité (par défaut: True)
            
        Returns:
            int: Nombre d'enregistrements exportés
        """
        try:
            if not data:
                self.logger.warning("Aucune donnée à exporter vers XML")
                return 0
            
            # Créer une copie profonde des données pour éviter de les altérer
            data_copy = []
            for item in data:
                # Convertir les valeurs en types Python standards
                item_copy = {}
                for key, value in item.items():
                    # Conversion des types spéciaux si nécessaire
                    if isinstance(value, bytes):
                        value = value.decode('utf-8', errors='replace')
                    # Convertir les valeurs en chaînes pour XML
                    if value is None:
                        value = ""
                    elif not isinstance(value, str):
                        value = str(value)
                    item_copy[key] = value
                data_copy.append(item_copy)
            
            # Créer l'élément racine
            root = ET.Element(root_element)
            
            # Ajouter chaque élément
            for item in data_copy:
                track_element = ET.SubElement(root, item_element)
                
                for key, value in item.items():
                    # Normaliser le nom de la balise XML (remplacer les espaces par des underscores)
                    tag_name = key.replace(' ', '_')
                    # Créer un élément pour chaque champ
                    field_element = ET.SubElement(track_element, tag_name)
                    field_element.text = value
            
            # Créer l'arbre XML
            tree = ET.ElementTree(root)
            
            # Formater le XML si demandé
            if pretty_print:
                xml_string = ET.tostring(root, encoding=encoding)
                dom = minidom.parseString(xml_string)
                pretty_xml = dom.toprettyxml(indent="  ", encoding=encoding)
                
                with open(file_path, 'wb') as f:
                    f.write(pretty_xml)
            else:
                tree.write(file_path, encoding=encoding, xml_declaration=True)
            
            self.logger.info(f"{len(data_copy)} enregistrements exportés vers {file_path}")
            return len(data_copy)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'export XML: {str(e)}")
            raise
