#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Interface graphique pour l'application MP3Tag Analyzer
Auteur: Geoffroy Streit
"""

import sys
import os
import logging
import sqlite3
import csv
from datetime import datetime

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QTabWidget, QLabel, QPushButton, QLineEdit, QComboBox,
                           QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                           QProgressBar, QStatusBar, QAction, QTextEdit, QListWidget,
                           QGroupBox, QFormLayout, QDialog, QDialogButtonBox, QCheckBox,
                           QSplitter, QFrame, QListWidgetItem, QInputDialog, QHeaderView, QSpinBox, QActionGroup)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QMetaObject, Q_ARG, QVariant
from PyQt5.QtGui import QIcon, QFont

from csv_parser import CSVParser
from db_manager import DatabaseManager
from db_exporter import DBExporter, MYSQL_AVAILABLE, POSTGRES_AVAILABLE
from format_exporter import FormatExporter

# Configuration du logging
logging.basicConfig(filename='mp3tag_analyzer.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class Worker(QThread):
    """Classe de travailleur pour exécuter des opérations en arrière-plan"""
    finished = pyqtSignal(object)
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.running = True
    
    def run(self):
        try:
            if self.running:
                result = self.func(*self.args, **self.kwargs)
                self.finished.emit(result)
        except Exception as e:
            if self.running:
                self.error.emit(str(e))
                traceback.print_exc()
    
    def stop(self):
        """Arrêter le thread proprement"""
        self.running = False


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""
    
    def __init__(self):
        """Initialisation de la fenêtre principale"""
        super().__init__()
        
        # Initialisation des attributs
        self.csv_parser = CSVParser()
        self.db_manager = DatabaseManager()
        self.current_data = []
        self.current_filtered_data = []
        self.headers = []
        self.active_workers = []  # Liste pour suivre les workers actifs
        self.logger = logging.getLogger('mp3tag_analyzer.gui')
        self.current_csv_path = None
        self.current_db_path = None  # Attribut pour stocker le chemin de la base de données actuelle
        
        # Mode d'affichage des colonnes (automatique, minimal, moyen, large)
        self.column_width_mode = "automatique"  # Par défaut: automatique
        self.column_widths = {
            "minimal": 80,
            "moyen": 150,
            "large": 250
        }
        
        # Configuration de la fenêtre
        self.setWindowTitle("MP3Tag Analyzer")
        self.setMinimumSize(1200, 800)
        
        # Initialisation de l'interface
        self._init_ui()
        
        # Connexion initiale à une base de données temporaire
        self.db_manager.connect()
        self.db_manager.create_tables()
        
        self.logger.info("Interface initialisée")

    def _init_ui(self):
        """Initialisation des composants de l'interface"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Création de la barre de menu
        self._create_menu_bar()
        
        # Groupe pour les actions de fichier
        file_group = QGroupBox("Fichiers")
        file_layout = QHBoxLayout(file_group)
        
        # Boutons pour charger un fichier CSV et une base de données
        self.btn_load_csv = QPushButton("Charger CSV")
        self.btn_load_csv.clicked.connect(self._load_csv_file)
        
        self.btn_load_db = QPushButton("Charger Base de Données")
        self.btn_load_db.clicked.connect(self._load_database)
        
        self.btn_save_db = QPushButton("Enregistrer Base de Données")
        self.btn_save_db.clicked.connect(self._save_database)
        
        file_layout.addWidget(self.btn_load_csv)
        file_layout.addWidget(self.btn_load_db)
        file_layout.addWidget(self.btn_save_db)
        
        # Groupe pour la recherche
        search_group = QGroupBox("Recherche")
        search_layout = QVBoxLayout(search_group)
        
        # Champ de recherche
        search_input_layout = QHBoxLayout()
        self.search_column = QComboBox()
        self.search_column.addItem("Tous les champs", "all")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher...")
        self.search_input.returnPressed.connect(self._search_data)
        
        search_button = QPushButton("Rechercher")
        search_button.clicked.connect(self._search_data)
        
        reset_search_button = QPushButton("Réinitialiser filtres")
        reset_search_button.clicked.connect(self._reset_filters)
        
        reset_data_button = QPushButton("Réinitialiser données")
        reset_data_button.clicked.connect(self._reset_data)
        
        search_input_layout.addWidget(QLabel("Rechercher dans:"))
        search_input_layout.addWidget(self.search_column)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(search_button)
        search_input_layout.addWidget(reset_search_button)
        search_input_layout.addWidget(reset_data_button)
        
        search_layout.addLayout(search_input_layout)
        
        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        # Onglets pour les différentes vues
        self.tab_widget = QTabWidget()
        
        # Tableau pour afficher les données
        self.data_widget = QWidget()
        data_layout = QVBoxLayout(self.data_widget)
        
        # Ajout du tableau et des contrôles de tri
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_widget.horizontalHeader().setStretchLastSection(True)
        self.table_widget.setSortingEnabled(True)  # Activer le tri
        self.table_widget.horizontalHeader().sectionClicked.connect(self._sort_table)
        
        # Ajouter le widget de données à l'onglet
        data_layout.addWidget(self.table_widget)
        self.tab_widget.addTab(self.data_widget, "Données")
        
        # Onglet SQL
        self.sql_widget = QWidget()
        sql_layout = QVBoxLayout(self.sql_widget)
        
        # Champ de saisie SQL
        self.sql_query = QTextEdit()
        self.sql_query.setPlaceholderText("Entrez votre requête SQL ici...")
        
        # Zone des presets SQL avec catégories
        preset_group = QGroupBox("Requêtes préenregistrées")
        preset_layout = QVBoxLayout(preset_group)
        
        # Combobox pour sélectionner la catégorie
        self.category_selector = QComboBox()
        
        # Liste pour afficher les presets de la catégorie sélectionnée
        self.preset_list = QListWidget()
        
        # Définir les catégories et les requêtes SQL prédéfinies
        self.sql_presets_by_category = {
            "Requêtes générales": {
                "Tous les morceaux": "SELECT * FROM mp3_files ORDER BY artist, album, title",
                "Nombre total de morceaux": "SELECT COUNT(*) as total_tracks FROM mp3_files",
                "Durée totale de la collection": "SELECT SUM(audio_length)/60 as total_minutes FROM mp3_files"
            },
            "Analyse par artiste": {
                "Artistes par nombre de morceaux": "SELECT artist, COUNT(*) as nb_tracks FROM mp3_files GROUP BY artist ORDER BY nb_tracks DESC",
                "Artistes avec un seul morceau": "SELECT artist, title FROM mp3_files WHERE artist IN (SELECT artist FROM mp3_files GROUP BY artist HAVING COUNT(*) = 1)",
                "Top 10 des artistes": "SELECT artist, COUNT(*) as nb_tracks FROM mp3_files GROUP BY artist ORDER BY nb_tracks DESC LIMIT 10"
            },
            "Analyse par album": {
                "Albums par année": "SELECT album, artist, year FROM mp3_files GROUP BY album ORDER BY year DESC",
                "Albums avec peu de morceaux": "SELECT album, artist, COUNT(*) as nb_tracks FROM mp3_files GROUP BY album, artist HAVING nb_tracks < 5 ORDER BY nb_tracks",
                "Albums les plus complets": "SELECT album, artist, COUNT(*) as nb_tracks FROM mp3_files GROUP BY album, artist ORDER BY nb_tracks DESC LIMIT 20"
            },
            "Durée et taille": {
                "Morceaux les plus longs": "SELECT title, artist, album, audio_length/60.0 as minutes FROM mp3_files ORDER BY audio_length DESC LIMIT 50",
                "Morceaux les plus courts": "SELECT title, artist, album, audio_length/60.0 as minutes FROM mp3_files WHERE audio_length > 0 ORDER BY audio_length ASC LIMIT 50",
                "Fichiers les plus volumineux": "SELECT title, artist, album, file_size FROM mp3_files ORDER BY CAST(REPLACE(file_size, ' KB', '') AS NUMERIC) DESC LIMIT 50"
            },
            "Métadonnées": {
                "Morceaux sans ISRC": "SELECT title, artist, album FROM mp3_files WHERE isrc IS NULL OR isrc = ''",
                "Morceaux sans année": "SELECT title, artist, album FROM mp3_files WHERE year IS NULL OR year = 0 OR year = ''",
                "Distribution des genres": "SELECT genre, COUNT(*) as nb_tracks FROM mp3_files GROUP BY genre ORDER BY nb_tracks DESC"
            },
            "Formats audio": {
                "Distribution des codecs": "SELECT codec, COUNT(*) as nb_tracks FROM mp3_files GROUP BY codec ORDER BY nb_tracks DESC",
                "Distribution des bitrates": "SELECT bitrate, COUNT(*) as nb_tracks FROM mp3_files GROUP BY bitrate ORDER BY nb_tracks DESC",
                "Fichiers avec VBR": "SELECT title, artist, album, bitrate FROM mp3_files WHERE vbr = '1' OR vbr = 'true' OR vbr = 'True'"
            },
            "Dates": {
                "Morceaux récemment importés": "SELECT title, artist, album, import_date FROM mp3_files ORDER BY import_date DESC LIMIT 50",
                "Fichiers les plus récents": "SELECT title, artist, album, file_create_date FROM mp3_files ORDER BY file_create_date DESC LIMIT 50",
                "Fichiers les plus anciens": "SELECT title, artist, album, file_create_date FROM mp3_files ORDER BY file_create_date ASC LIMIT 50"
            }
        }
        
        # Ajouter les catégories au sélecteur
        for category in self.sql_presets_by_category.keys():
            self.category_selector.addItem(category)
        
        # Connecter le changement de catégorie à la mise à jour de la liste des presets
        self.category_selector.currentTextChanged.connect(self._update_preset_list)
        self.preset_list.itemClicked.connect(self._load_sql_preset)
        
        # Initialiser la liste des presets avec la première catégorie
        self._update_preset_list(list(self.sql_presets_by_category.keys())[0])
        
        # Bouton pour exécuter la requête SQL
        self.btn_execute_sql = QPushButton("Exécuter")
        self.btn_execute_sql.clicked.connect(self._execute_sql)
        
        # Bouton pour sauvegarder un preset
        self.btn_save_preset = QPushButton("Sauvegarder comme preset")
        self.btn_save_preset.clicked.connect(self._save_sql_preset)
        
        # Ajouter les widgets à l'onglet SQL
        preset_layout.addWidget(QLabel("Catégorie:"))
        preset_layout.addWidget(self.category_selector)
        preset_layout.addWidget(QLabel("Requêtes disponibles:"))
        preset_layout.addWidget(self.preset_list)
        
        sql_button_layout = QHBoxLayout()
        sql_button_layout.addWidget(self.btn_execute_sql)
        sql_button_layout.addWidget(self.btn_save_preset)
        
        sql_layout.addWidget(preset_group)
        sql_layout.addWidget(QLabel("Requête SQL:"))
        sql_layout.addWidget(self.sql_query)
        sql_layout.addLayout(sql_button_layout)
        
        self.tab_widget.addTab(self.sql_widget, "Requêtes SQL")
        
        # Barre de statut
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Prêt")
        
        # Ajout des widgets au layout principal
        main_layout.addWidget(file_group)
        main_layout.addWidget(search_group)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.tab_widget, 1)  # 1 = stretch factor
    
    def _create_menu_bar(self):
        """Création de la barre de menu"""
        menu_bar = self.menuBar()
        
        # Menu Fichier
        file_menu = menu_bar.addMenu("Fichier")
        
        # Chargement CSV
        load_csv_action = QAction("Charger CSV", self)
        load_csv_action.triggered.connect(self._load_csv_file)
        file_menu.addAction(load_csv_action)
        
        # Chargement Base
        load_db_action = QAction("Charger Base de Données", self)
        load_db_action.triggered.connect(self._load_database)
        file_menu.addAction(load_db_action)
        
        # Enregistrement Base
        save_db_action = QAction("Enregistrer Base de Données", self)
        save_db_action.triggered.connect(self._save_database)
        file_menu.addAction(save_db_action)
        
        # Séparateur
        file_menu.addSeparator()
        
        # Sous-menu Export
        export_menu = file_menu.addMenu("Exporter vers...")
        
        # Export MySQL
        if MYSQL_AVAILABLE:
            export_mysql_action = QAction("MySQL", self)
            export_mysql_action.triggered.connect(self._export_to_mysql)
            export_menu.addAction(export_mysql_action)
        else:
            export_mysql_disabled = QAction("MySQL (non disponible)", self)
            export_mysql_disabled.setEnabled(False)
            export_menu.addAction(export_mysql_disabled)
        
        # Export PostgreSQL
        if POSTGRES_AVAILABLE:
            export_postgres_action = QAction("PostgreSQL", self)
            export_postgres_action.triggered.connect(self._export_to_postgres)
            export_menu.addAction(export_postgres_action)
        else:
            export_postgres_disabled = QAction("PostgreSQL (non disponible)", self)
            export_postgres_disabled.setEnabled(False)
            export_menu.addAction(export_postgres_disabled)
        
        # Séparateur dans le sous-menu Export
        export_menu.addSeparator()
        
        # Export CSV
        export_csv_action = QAction("CSV", self)
        export_csv_action.triggered.connect(self._export_to_csv)
        export_menu.addAction(export_csv_action)
        
        # Export JSON
        export_json_action = QAction("JSON", self)
        export_json_action.triggered.connect(self._export_to_json)
        export_menu.addAction(export_json_action)
        
        # Export XML
        export_xml_action = QAction("XML", self)
        export_xml_action.triggered.connect(self._export_to_xml)
        export_menu.addAction(export_xml_action)
        
        # Séparateur
        file_menu.addSeparator()
        
        # Quitter
        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Édition
        edit_menu = menu_bar.addMenu("Édition")
        
        # Sous-menu Largeur des colonnes
        column_width_menu = edit_menu.addMenu("Largeur des colonnes")
        
        # Options de largeur
        auto_width_action = QAction("Automatique", self)
        auto_width_action.triggered.connect(lambda: self._set_column_width_mode("automatique"))
        auto_width_action.setCheckable(True)
        auto_width_action.setChecked(self.column_width_mode == "automatique")
        
        min_width_action = QAction("Minimale", self)
        min_width_action.triggered.connect(lambda: self._set_column_width_mode("minimal"))
        min_width_action.setCheckable(True)
        min_width_action.setChecked(self.column_width_mode == "minimal")
        
        med_width_action = QAction("Moyenne", self)
        med_width_action.triggered.connect(lambda: self._set_column_width_mode("moyen"))
        med_width_action.setCheckable(True)
        med_width_action.setChecked(self.column_width_mode == "moyen")
        
        max_width_action = QAction("Grande", self)
        max_width_action.triggered.connect(lambda: self._set_column_width_mode("large"))
        max_width_action.setCheckable(True)
        max_width_action.setChecked(self.column_width_mode == "large")
        
        # Groupe d'actions pour les options de largeur
        self.column_width_action_group = QActionGroup(self)
        self.column_width_action_group.addAction(auto_width_action)
        self.column_width_action_group.addAction(min_width_action)
        self.column_width_action_group.addAction(med_width_action)
        self.column_width_action_group.addAction(max_width_action)
        self.column_width_action_group.setExclusive(True)
        
        column_width_menu.addAction(auto_width_action)
        column_width_menu.addAction(min_width_action)
        column_width_menu.addAction(med_width_action)
        column_width_menu.addAction(max_width_action)
        
        # Menu Aide
        help_menu = menu_bar.addMenu("Aide")
        
        # À propos
        about_action = QAction("À propos", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _set_column_width_mode(self, mode):
        """Définit le mode d'affichage des colonnes"""
        self.column_width_mode = mode
        
        if mode == "automatique":
            self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        else:
            width = self.column_widths[mode]
            for i in range(self.table_widget.columnCount()):
                self.table_widget.setColumnWidth(i, width)

    def _load_csv_file(self):
        """Chargement d'un fichier CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier CSV",
            "",
            "Fichiers CSV (*.csv);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.status_bar.showMessage(f"Chargement du fichier {file_path}...")
            self.progress_bar.setVisible(True)
            
            # Création d'un worker pour charger le fichier CSV
            worker = Worker(self.csv_parser.parse_file, file_path)
            worker.finished.connect(self._update_table_from_worker)
            worker.error.connect(self._handle_error)
            worker.start()
            self.active_workers.append(worker)
    
    def _update_table_from_worker(self, result):
        """Mise à jour du tableau avec les données chargées par le worker"""
        self.progress_bar.setVisible(False)
        
        if result:
            self.headers, self.current_data = result
            
            # Mise à jour du tableau
            self._update_table()
            
            # Mise à jour des options de recherche
            self.search_column.clear()
            self.search_column.addItem("Tous les champs", "all")
            for header in self.headers:
                self.search_column.addItem(header, header)
            
            # Insertion des données dans la base de données
            worker = Worker(self._insert_data_to_db)
            worker.finished.connect(self._data_inserted_handler)  # Utilisez le nouveau gestionnaire
            worker.error.connect(self._handle_error)
            worker.start()
            self.active_workers.append(worker)
            
            self.status_bar.showMessage(f"{len(self.current_data)} enregistrements chargés")
        else:
            QMessageBox.warning(self, "Erreur", "Aucune donnée n'a pu être chargée")
            self.status_bar.showMessage("Erreur lors du chargement des données")
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)
    
    def _insert_data_to_db(self):
        """Méthode pour insérer les données dans la base de données dans un thread séparé
        Cette méthode s'exécute dans un thread séparé, elle ne doit donc pas manipuler directement l'interface
        """
        try:
            # Mémoriser l'ancienne connexion
            old_conn = self.db_manager.conn
            old_cursor = self.db_manager.cursor
            
            # Réutiliser le gestionnaire existant mais avec une nouvelle connexion pour thread-safety
            if self.current_db_path:
                self.db_manager.connect(self.current_db_path)
            else:
                self.db_manager.connect()
            
            # Créer les tables si nécessaire
            self.db_manager.create_tables()
            
            # Insertion des données avec vérification d'unicité
            records_inserted = self.db_manager.insert_records(self.current_data)
            
            # Fermer la connexion temporaire et restaurer l'ancienne
            self.db_manager.close()
            
            # Restaurer l'ancienne connexion
            self.db_manager.conn = old_conn
            self.db_manager.cursor = old_cursor
            
            return records_inserted
        except Exception as e:
            raise Exception(f"Erreur lors de l'insertion des données: {str(e)}")
    
    def _handle_error(self, error):
        """Gestion des erreurs"""
        QMessageBox.critical(self, "Erreur", error)
        self.status_bar.showMessage("Erreur")
        self.progress_bar.setVisible(False)
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)
    
    def _load_database(self):
        """Chargement d'une base de données SQLite"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir une base de données SQLite",
            "",
            "Bases de données SQLite (*.db *.sqlite);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.status_bar.showMessage(f"Chargement de la base de données {file_path}...")
            self.progress_bar.setVisible(True)
            
            # Fermeture de la connexion actuelle
            self.db_manager.close()
            
            # Ouverture de la nouvelle base de données
            if self.db_manager.connect(file_path):
                self.current_db_path = file_path  # Mettre à jour le chemin de la base de données actuelle
                # Récupération des données
                data = self.db_manager.get_all_records()
                
                if data:
                    self.current_data = data
                    
                    # Extraction des entêtes
                    self.headers = list(data[0].keys())
                    
                    # Mise à jour du tableau
                    self._update_table()
                    
                    # Mise à jour des options de recherche
                    self.search_column.clear()
                    self.search_column.addItem("Tous les champs", "all")
                    for header in self.headers:
                        self.search_column.addItem(header, header)
                    
                    self.status_bar.showMessage(f"{len(data)} enregistrements chargés")
                else:
                    QMessageBox.warning(self, "Avertissement", "La base de données est vide ou n'a pas pu être lue")
                    self.status_bar.showMessage("Base de données vide")
            else:
                QMessageBox.warning(self, "Erreur", f"Impossible de charger la base de données {file_path}")
                self.status_bar.showMessage("Erreur lors du chargement de la base de données")
            
            self.progress_bar.setVisible(False)
    
    def _save_database(self):
        """Enregistrement de la base de données SQLite"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à enregistrer")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Enregistrer la base de données",
            "",
            "Bases de données SQLite (*.db *.sqlite);;Tous les fichiers (*)"
        )
        
        if file_path:
            # Si l'extension n'est pas spécifiée, ajouter .db
            if not file_path.endswith(('.db', '.sqlite')):
                file_path += '.db'
            
            self.status_bar.showMessage(f"Enregistrement de la base de données {file_path}...")
            self.progress_bar.setVisible(True)
            
            # Création d'un worker pour enregistrer la base de données
            # Nous allons utiliser une fonction lambda pour passer les paramètres
            worker = Worker(lambda: self._save_database_to_file(file_path))
            worker.finished.connect(self._database_saved)
            worker.error.connect(self._handle_error)
            worker.start()
            self.active_workers.append(worker)
    
    def _save_database_to_file(self, file_path):
        """Sauvegarde la base de données dans un fichier depuis un thread séparé"""
        try:
            # Créer une instance pour ce thread qui utilise la base courante (où les données ont été insérées)
            db = DatabaseManager()
            
            # Se connecter à la base courante (temporaire) pour récupérer les données
            if self.current_db_path:
                db.connect(self.current_db_path)
            else:
                db.connect()  # Base temporaire par défaut
                
            db.create_tables()
            
            # Récupération de toutes les données de la base courante
            data = db.get_all_records()
            
            # Fermeture de la connexion temporaire
            db.close()
            
            # Si aucune donnée n'a été récupérée, utiliser les données en mémoire
            if not data and self.current_data:
                data = self.current_data
            
            # Création d'une nouvelle connection vers le fichier cible
            target_db = DatabaseManager()
            target_db.connect(file_path)
            target_db.create_tables()
            
            # Insertion des données dans la nouvelle base
            records_inserted = target_db.insert_records(data)
            
            # Fermeture de la connexion
            target_db.close()
            
            # Mettre à jour le chemin de la base de données courante
            self.current_db_path = file_path
            
            return records_inserted
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise Exception(f"Erreur lors de la sauvegarde de la base de données: {str(e)}")
    
    def _database_saved(self, result):
        """Mise à jour après enregistrement de la base de données"""
        if result:
            QMessageBox.information(self, "Succès", f"Base de données enregistrée avec succès dans {result}")
            self.status_bar.showMessage(f"Base de données enregistrée dans {result}")
        else:
            QMessageBox.warning(self, "Erreur", "Erreur lors de l'enregistrement de la base de données")
            self.status_bar.showMessage("Erreur lors de l'enregistrement de la base de données")
        
        self.progress_bar.setVisible(False)
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)
    
    def _update_table(self, data=None):
        """Mise à jour du tableau avec les données actuelles"""
        if data is None:
            data = self.current_data
            
        if not data:
            self.table_widget.setRowCount(0)
            return
        
        # Mise à jour des en-têtes si nécessaire
        if not self.headers:
            # Utiliser les clés du premier élément comme en-têtes
            self.headers = list(data[0].keys())
        
        # Configuration du tableau
        self.table_widget.setRowCount(len(data))
        self.table_widget.setColumnCount(len(self.headers))
        self.table_widget.setHorizontalHeaderLabels(self.headers)
        
        # Déconnexion temporaire du signal itemChanged pour éviter les appels pendant le remplissage
        try:
            self.table_widget.itemChanged.disconnect(self._cell_changed)
        except:
            pass
        
        # Remplissage du tableau
        for row_idx, row_data in enumerate(data):
            for col_idx, header in enumerate(self.headers):
                # Récupération de la valeur
                value = ""
                
                # Vérifier si la clé existe directement
                if header in row_data:
                    value = row_data[header]
                else:
                    # Essayer avec la clé normalisée (snake_case)
                    normalized_key = header.lower().replace(' ', '_')
                    if normalized_key in row_data:
                        value = row_data[normalized_key]
                
                # Formatage spécial pour certains champs
                if header == "AudioLength" and value:
                    try:
                        # Conversion des secondes en format h:m:s
                        seconds = int(float(value))
                        hours, remainder = divmod(seconds, 3600)
                        minutes, seconds = divmod(remainder, 60)
                        if hours > 0:
                            value = f"{hours}:{minutes:02d}:{seconds:02d}"
                        else:
                            value = f"{minutes:02d}:{seconds:02d}"
                    except (ValueError, TypeError):
                        # En cas d'erreur, garder la valeur originale
                        pass
                
                # Création de l'item
                item = QTableWidgetItem(str(value))
                # Rendre l'item éditable
                item.setFlags(item.flags() | Qt.ItemIsEditable)
                
                # Stocker les données brutes pour le tri
                if isinstance(value, (int, float)):
                    item.setData(Qt.UserRole, value)  # Stocker la valeur numérique pour le tri
                
                # Ajout de l'item au tableau
                self.table_widget.setItem(row_idx, col_idx, item)
        
        # Ajustement des colonnes selon le mode sélectionné
        if self.column_width_mode == "automatique":
            self.table_widget.resizeColumnsToContents()
        else:
            width = self.column_widths[self.column_width_mode]
            for i in range(self.table_widget.columnCount()):
                self.table_widget.setColumnWidth(i, width)
        
        # Reconnexion du signal de modification des cellules
        self.table_widget.itemChanged.connect(self._cell_changed)

    def _sort_table(self, column_index):
        """Trie le tableau selon la colonne cliquée"""
        # L'en-tête du tableau gère automatiquement le tri
        self.status_bar.showMessage(f"Tri par {self.headers[column_index]}")
    
    def _execute_sql(self):
        """Exécute une requête SQL personnalisée"""
        sql_query = self.sql_query.toPlainText().strip()
        
        if not sql_query:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une requête SQL")
            return
        
        # Création d'un worker pour exécuter la requête SQL
        worker = Worker(self._execute_sql_query, sql_query)
        worker.finished.connect(self._display_sql_results)
        worker.error.connect(self._handle_sql_error)
        worker.start()
        self.active_workers.append(worker)
        
        self.status_bar.showMessage("Exécution de la requête SQL...")
        self.progress_bar.setVisible(True)
    
    def _execute_sql_query(self, query):
        """Exécute une requête SQL dans un thread séparé"""
        try:
            # Utiliser le gestionnaire de base de données avec le chemin actuel de DB
            db = DatabaseManager()
            db.connect(self.current_db_path)  # Utiliser le chemin actuel de la base
            db.create_tables()
            
            # Exécuter la requête SQL
            conn = db.conn
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Récupérer les résultats
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description] if cursor.description else []
            
            # Convertir les résultats en liste de dictionnaires
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            
            db.close()
            return columns, results
        except sqlite3.Error as e:
            raise Exception(f"Erreur SQL: {str(e)}")
    
    def _display_sql_results(self, result):
        """Affiche les résultats d'une requête SQL"""
        self.progress_bar.setVisible(False)
        
        if result:
            columns, data = result
            
            if data and columns:
                # Mise à jour des en-têtes
                self.headers = columns
                self.current_data = data
                
                # Mise à jour du tableau
                self._update_table(data)
                
                self.status_bar.showMessage(f"Requête exécutée avec succès: {len(data)} enregistrements")
                
                # Basculer vers l'onglet Données pour afficher les résultats
                self.tab_widget.setCurrentIndex(0)
            else:
                QMessageBox.information(self, "Résultat", "La requête n'a retourné aucun résultat ou a été exécutée avec succès sans résultats.")
                self.status_bar.showMessage("Requête exécutée sans résultats")
        else:
            QMessageBox.warning(self, "Erreur", "Erreur lors de l'exécution de la requête")
            self.status_bar.showMessage("Erreur lors de l'exécution de la requête")
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)
    
    def _handle_sql_error(self, error):
        """Gestion des erreurs SQL"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erreur SQL", error)
        self.status_bar.showMessage("Erreur SQL")
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)
    
    def _update_preset_list(self, category):
        """Met à jour la liste des presets selon la catégorie sélectionnée"""
        self.preset_list.clear()
        
        if category in self.sql_presets_by_category:
            for preset_name in self.sql_presets_by_category[category].keys():
                self.preset_list.addItem(preset_name)
    
    def _load_sql_preset(self, item):
        """Charge un preset SQL"""
        preset_name = item.text()
        category = self.category_selector.currentText()
        
        if category in self.sql_presets_by_category and preset_name in self.sql_presets_by_category[category]:
            self.sql_query.setText(self.sql_presets_by_category[category][preset_name])
            self.status_bar.showMessage(f"Preset SQL '{preset_name}' chargé")
    
    def _save_sql_preset(self):
        """Sauvegarde un preset SQL"""
        query = self.sql_query.toPlainText().strip()
        
        if not query:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une requête SQL à sauvegarder")
            return
        
        # Demander le nom du preset
        name, ok = QInputDialog.getText(self, "Sauvegarder le preset", "Nom du preset:")
        if not (ok and name):
            return
        
        # Demander la catégorie
        categories = list(self.sql_presets_by_category.keys())
        categories.append("Nouvelle catégorie...")
        category, ok = QInputDialog.getItem(self, "Catégorie du preset", "Choisissez une catégorie:", categories, 0, False)
        if not ok:
            return
        
        # Si nouvelle catégorie, demander le nom
        if category == "Nouvelle catégorie...":
            category, ok = QInputDialog.getText(self, "Nouvelle catégorie", "Nom de la nouvelle catégorie:")
            if not (ok and category):
                return
            # Créer la nouvelle catégorie
            if category not in self.sql_presets_by_category:
                self.sql_presets_by_category[category] = {}
                self.category_selector.addItem(category)
        
        # Ajouter le preset à la catégorie
        self.sql_presets_by_category[category][name] = query
        
        # Mettre à jour l'interface
        current_category = self.category_selector.currentText()
        if current_category == category:
            self._update_preset_list(category)
        
        # Sélectionner la catégorie du nouveau preset
        index = self.category_selector.findText(category)
        if index >= 0:
            self.category_selector.setCurrentIndex(index)
        
        self.status_bar.showMessage(f"Preset SQL '{name}' sauvegardé dans la catégorie '{category}'")
    
    def _search_data(self):
        """Recherche dans les données selon les critères"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à rechercher")
            return
        
        search_text = self.search_input.text().strip()
        search_column = self.search_column.currentData()
        
        if not search_text:
            # Si la recherche est vide, afficher toutes les données
            self.current_filtered_data = self.current_data
            self._update_table()
            self.status_bar.showMessage(f"Affichage de tous les enregistrements ({len(self.current_data)})")
            return
        
        # Recherche dans les données
        filtered_data = []
        
        for record in self.current_data:
            if search_column == "all":
                # Recherche dans tous les champs
                for key, value in record.items():
                    if isinstance(value, str) and search_text.lower() in value.lower():
                        filtered_data.append(record)
                        break
            else:
                # Recherche dans une colonne spécifique
                if search_column in record:
                    value = record[search_column]
                    if isinstance(value, str) and search_text.lower() in value.lower():
                        filtered_data.append(record)
                else:
                    # Essayer avec la clé normalisée
                    normalized_key = search_column.lower().replace(' ', '_')
                    if normalized_key in record:
                        value = record[normalized_key]
                        if isinstance(value, str) and search_text.lower() in value.lower():
                            filtered_data.append(record)
        
        # Mise à jour du tableau avec les résultats
        self.current_filtered_data = filtered_data
        self._update_table(filtered_data)
        
        # Mise à jour de la barre de statut
        if filtered_data:
            self.status_bar.showMessage(f"{len(filtered_data)} enregistrement(s) trouvé(s)")
        else:
            QMessageBox.information(self, "Résultats", "Aucun enregistrement ne correspond aux critères de recherche")
            self.status_bar.showMessage("Aucun résultat")

    def _reset_filters(self):
        """Réinitialise les filtres"""
        self.search_input.clear()
        self.search_column.setCurrentIndex(0)
        self.current_filtered_data = self.current_data
        self._update_table()
        self.status_bar.showMessage(f"Affichage de tous les enregistrements ({len(self.current_data)})")
    
    def _reset_data(self):
        """Réinitialise les données"""
        self.current_data = []
        self.headers = []
        self.current_filtered_data = []
        self._update_table()
        self.status_bar.showMessage("Données réinitialisées")
    
    def _show_about(self):
        """Affichage de la boîte de dialogue À propos"""
        QMessageBox.about(
            self,
            "À propos",
            f"""<b>MP3Tag Analyzer</b>
            <p>Version 1.5.0</p>
            <p>Auteur: Geoffroy Streit</p>
            <p>Date: {datetime.now().strftime('%d/%m/%Y')}</p>
            <p>Un programme pour analyser les fichiers CSV générés par MP3tag et les stocker dans une base de données SQLite.</p>
            <p><b>Fonctionnalités principales:</b></p>
            <ul>
                <li>Chargement de fichiers CSV générés par MP3tag (UTF-8, UTF-16-LE)</li>
                <li>Détection automatique de l'encodage et du séparateur</li>
                <li>Stockage des données dans une base SQLite</li>
                <li>Recherche avancée par critères multiples</li>
                <li>Exécution de requêtes SQL personnalisées</li>
                <li>Export vers MySQL et PostgreSQL</li>
                <li>Export vers formats standards: CSV, JSON, XML</li>
                <li>Édition des métadonnées directement dans l'interface</li>
            </ul>
            <p>Développé avec PyQt5 et SQLite.</p>
            """
        )
    
    def closeEvent(self, event):
        """Gestion de la fermeture de l'application"""
        # Arrêter tous les workers actifs
        for worker in self.active_workers:
            worker.stop()
            worker.wait()  # Attendre que le thread se termine
        
        # Fermer la connexion à la base de données
        if self.db_manager:
            self.db_manager.close()
        
        # Accepter l'événement de fermeture
        event.accept()

    def _data_inserted_handler(self, records_inserted):
        """Gestionnaire appelé après l'insertion des données dans la base
        Cette méthode s'exécute dans le thread principal et peut interagir avec l'interface
        """
        if records_inserted > 0:
            self.status_bar.showMessage(f"{records_inserted} enregistrements insérés dans la base de données")
            
            # Proposer de sauvegarder la base de données depuis le thread principal
            response = QMessageBox.question(
                self,
                "Données importées",
                f"{records_inserted} enregistrements ont été insérés dans la base temporaire. Voulez-vous enregistrer cette base de données sur disque ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if response == QMessageBox.Yes:
                # Appeler la méthode pour enregistrer la base de données
                self._save_database()
        else:
            self.status_bar.showMessage("Aucun enregistrement inséré")
            QMessageBox.warning(self, "Information", "Aucun enregistrement n'a pu être inséré dans la base de données.")
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)

    def _export_to_mysql(self):
        """Exporte les données vers une base MySQL"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter. Veuillez d'abord charger un fichier CSV ou une base de données.")
            return
            
        # Vérification de la disponibilité du module MySQL
        if not MYSQL_AVAILABLE:
            QMessageBox.critical(self, "Erreur", "Le module MySQL n'est pas disponible. Veuillez installer mysql-connector-python.")
            return
        
        # Boîte de dialogue de configuration MySQL
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration de l'export MySQL")
        layout = QFormLayout(dialog)
        
        # Champs de configuration
        host_input = QLineEdit("localhost")
        port_input = QLineEdit("3306")
        user_input = QLineEdit("root")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        database_input = QLineEdit("mp3tag_analyzer")
        table_input = QLineEdit("mp3_tags")
        
        layout.addRow("Hôte:", host_input)
        layout.addRow("Port:", port_input)
        layout.addRow("Utilisateur:", user_input)
        layout.addRow("Mot de passe:", password_input)
        layout.addRow("Base de données:", database_input)
        layout.addRow("Table:", table_input)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Récupération des valeurs de configuration
            config = {
                'host': host_input.text(),
                'port': int(port_input.text()),
                'user': user_input.text(),
                'password': password_input.text(),
                'database': database_input.text(),
                'table': table_input.text()
            }
            
            # Mise à jour de la barre de statut et affichage de la barre de progression
            self.status_bar.showMessage("Exportation vers MySQL en cours...")
            self.progress_bar.setVisible(True)
            
            # Création du worker pour l'exportation
            worker = Worker(lambda: self._do_mysql_export(config))
            worker.finished.connect(lambda count: self._export_completed("MySQL", count))
            worker.error.connect(self._handle_error)
            worker.start()
            self.active_workers.append(worker)
    
    def _export_to_postgres(self):
        """Exporte les données vers une base PostgreSQL"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter. Veuillez d'abord charger un fichier CSV ou une base de données.")
            return
            
        # Vérification de la disponibilité du module PostgreSQL
        if not POSTGRES_AVAILABLE:
            QMessageBox.critical(self, "Erreur", "Le module PostgreSQL n'est pas disponible. Veuillez installer psycopg2-binary.")
            return
        
        # Boîte de dialogue de configuration PostgreSQL
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration de l'export PostgreSQL")
        layout = QFormLayout(dialog)
        
        # Champs de configuration
        host_input = QLineEdit("localhost")
        port_input = QLineEdit("5432")
        user_input = QLineEdit("postgres")
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        database_input = QLineEdit("mp3tag_analyzer")
        table_input = QLineEdit("mp3_tags")
        
        layout.addRow("Hôte:", host_input)
        layout.addRow("Port:", port_input)
        layout.addRow("Utilisateur:", user_input)
        layout.addRow("Mot de passe:", password_input)
        layout.addRow("Base de données:", database_input)
        layout.addRow("Table:", table_input)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Récupération des valeurs de configuration
            config = {
                'host': host_input.text(),
                'port': int(port_input.text()),
                'user': user_input.text(),
                'password': password_input.text(),
                'database': database_input.text(),
                'table': table_input.text()
            }
            
            # Mise à jour de la barre de statut et affichage de la barre de progression
            self.status_bar.showMessage("Exportation vers PostgreSQL en cours...")
            self.progress_bar.setVisible(True)
            
            # Création du worker pour l'exportation
            worker = Worker(lambda: self._do_postgres_export(config))
            worker.finished.connect(lambda count: self._export_completed("PostgreSQL", count))
            worker.error.connect(self._handle_error)
            worker.start()
            self.active_workers.append(worker)
    
    def _do_mysql_export(self, config):
        """Effectue l'exportation vers MySQL dans un thread séparé"""
        try:
            exporter = DBExporter()
            
            # Si nous avons un chemin de base de données SQLite, l'utiliser pour l'export
            if self.current_db_path:
                return exporter.export_from_sqlite(self.current_db_path, 'mysql', config)
            else:
                # Sinon, utiliser les données en mémoire
                return exporter.export_to_mysql(self.current_data, config)
        except Exception as e:
            raise Exception(f"Erreur lors de l'exportation vers MySQL: {str(e)}")
    
    def _do_postgres_export(self, config):
        """Effectue l'exportation vers PostgreSQL dans un thread séparé"""
        try:
            exporter = DBExporter()
            
            # Si nous avons un chemin de base de données SQLite, l'utiliser pour l'export
            if self.current_db_path:
                return exporter.export_from_sqlite(self.current_db_path, 'postgres', config)
            else:
                # Sinon, utiliser les données en mémoire
                return exporter.export_to_postgres(self.current_data, config)
        except Exception as e:
            raise Exception(f"Erreur lors de l'exportation vers PostgreSQL: {str(e)}")
    
    def _export_completed(self, export_type, count):
        """Gestionnaire appelé après la fin de l'exportation"""
        self.progress_bar.setVisible(False)
        
        if count > 0:
            self.status_bar.showMessage(f"{count} enregistrements exportés vers {export_type}")
            QMessageBox.information(self, "Exportation réussie", f"{count} enregistrements ont été exportés avec succès vers {export_type}.")
        else:
            self.status_bar.showMessage(f"Aucun enregistrement exporté vers {export_type}")
            QMessageBox.warning(self, "Information", f"Aucun enregistrement n'a pu être exporté vers {export_type}.")
        
        # Retirer le worker de la liste des workers actifs
        sender = self.sender()
        if sender in self.active_workers:
            self.active_workers.remove(sender)

    def _export_to_csv(self):
        """Exporte les données vers un fichier CSV"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter. Veuillez d'abord charger un fichier CSV ou une base de données.")
            return
        
        # Boîte de dialogue de configuration CSV
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration de l'export CSV")
        layout = QFormLayout(dialog)
        
        # Champs de configuration
        delimiter_input = QComboBox()
        delimiter_input.addItem("Point-virgule (;)", ";")
        delimiter_input.addItem("Virgule (,)", ",")
        delimiter_input.addItem("Tabulation (\t)", "\t")
        
        encoding_input = QComboBox()
        encoding_input.addItem("UTF-8 avec BOM", "utf-8-sig")
        encoding_input.addItem("UTF-8", "utf-8")
        encoding_input.addItem("UTF-16-LE (MP3Tag)", "utf-16-le")
        encoding_input.addItem("ISO-8859-1", "iso-8859-1")
        
        include_headers_input = QCheckBox()
        include_headers_input.setChecked(True)
        
        layout.addRow("Séparateur:", delimiter_input)
        layout.addRow("Encodage:", encoding_input)
        layout.addRow("Inclure les en-têtes:", include_headers_input)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Demander le chemin du fichier de destination
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier CSV",
                "",
                "Fichiers CSV (*.csv);;Tous les fichiers (*)"
            )
            
            if file_path:
                # Si l'extension n'est pas spécifiée, ajouter .csv
                if not file_path.endswith('.csv'):
                    file_path += '.csv'
                
                # Récupération des valeurs de configuration
                config = {
                    'delimiter': delimiter_input.currentData(),
                    'encoding': encoding_input.currentData(),
                    'include_headers': include_headers_input.isChecked()
                }
                
                # Mise à jour de la barre de statut et affichage de la barre de progression
                self.status_bar.showMessage("Exportation vers CSV en cours...")
                self.progress_bar.setVisible(True)
                
                # Création du worker pour l'exportation
                worker = Worker(lambda: self._do_csv_export(file_path, config))
                worker.finished.connect(lambda count: self._export_completed("CSV", count))
                worker.error.connect(self._handle_error)
                worker.start()
                self.active_workers.append(worker)
    
    def _export_to_json(self):
        """Exporte les données vers un fichier JSON"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter. Veuillez d'abord charger un fichier CSV ou une base de données.")
            return
        
        # Boîte de dialogue de configuration JSON
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration de l'export JSON")
        layout = QFormLayout(dialog)
        
        # Champs de configuration
        encoding_input = QComboBox()
        encoding_input.addItem("UTF-8", "utf-8")
        encoding_input.addItem("UTF-16", "utf-16")
        
        indent_input = QSpinBox()
        indent_input.setRange(0, 8)
        indent_input.setValue(2)
        
        format_input = QComboBox()
        format_input.addItem("Tableau JSON", True)
        format_input.addItem("Objet JSON avec IDs", False)
        
        layout.addRow("Encodage:", encoding_input)
        layout.addRow("Indentation:", indent_input)
        layout.addRow("Format:", format_input)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Demander le chemin du fichier de destination
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier JSON",
                "",
                "Fichiers JSON (*.json);;Tous les fichiers (*)"
            )
            
            if file_path:
                # Si l'extension n'est pas spécifiée, ajouter .json
                if not file_path.endswith('.json'):
                    file_path += '.json'
                
                # Récupération des valeurs de configuration
                config = {
                    'encoding': encoding_input.currentData(),
                    'indent': indent_input.value(),
                    'as_array': format_input.currentData()
                }
                
                # Mise à jour de la barre de statut et affichage de la barre de progression
                self.status_bar.showMessage("Exportation vers JSON en cours...")
                self.progress_bar.setVisible(True)
                
                # Création du worker pour l'exportation
                worker = Worker(lambda: self._do_json_export(file_path, config))
                worker.finished.connect(lambda count: self._export_completed("JSON", count))
                worker.error.connect(self._handle_error)
                worker.start()
                self.active_workers.append(worker)
    
    def _export_to_xml(self):
        """Exporte les données vers un fichier XML"""
        if not self.current_data:
            QMessageBox.warning(self, "Erreur", "Aucune donnée à exporter. Veuillez d'abord charger un fichier CSV ou une base de données.")
            return
        
        # Boîte de dialogue de configuration XML
        dialog = QDialog(self)
        dialog.setWindowTitle("Configuration de l'export XML")
        layout = QFormLayout(dialog)
        
        # Champs de configuration
        encoding_input = QComboBox()
        encoding_input.addItem("UTF-8", "utf-8")
        encoding_input.addItem("UTF-16", "utf-16")
        
        root_element_input = QLineEdit("mp3collection")
        item_element_input = QLineEdit("track")
        
        pretty_print_input = QCheckBox()
        pretty_print_input.setChecked(True)
        
        layout.addRow("Encodage:", encoding_input)
        layout.addRow("Nom de l'élément racine:", root_element_input)
        layout.addRow("Nom de l'élément pour chaque piste:", item_element_input)
        layout.addRow("Formatage pour lisibilité:", pretty_print_input)
        
        # Boutons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            # Demander le chemin du fichier de destination
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Enregistrer le fichier XML",
                "",
                "Fichiers XML (*.xml);;Tous les fichiers (*)"
            )
            
            if file_path:
                # Si l'extension n'est pas spécifiée, ajouter .xml
                if not file_path.endswith('.xml'):
                    file_path += '.xml'
                
                # Récupération des valeurs de configuration
                config = {
                    'encoding': encoding_input.currentData(),
                    'root_element': root_element_input.text(),
                    'item_element': item_element_input.text(),
                    'pretty_print': pretty_print_input.isChecked()
                }
                
                # Mise à jour de la barre de statut et affichage de la barre de progression
                self.status_bar.showMessage("Exportation vers XML en cours...")
                self.progress_bar.setVisible(True)
                
                # Création du worker pour l'exportation
                worker = Worker(lambda: self._do_xml_export(file_path, config))
                worker.finished.connect(lambda count: self._export_completed("XML", count))
                worker.error.connect(self._handle_error)
                worker.start()
                self.active_workers.append(worker)
    
    def _do_csv_export(self, file_path, config):
        """Effectue l'exportation vers CSV dans un thread séparé"""
        try:
            exporter = FormatExporter()
            return exporter.export_to_csv(
                self.current_data, 
                file_path,
                delimiter=config['delimiter'],
                encoding=config['encoding'],
                include_headers=config['include_headers']
            )
        except Exception as e:
            raise Exception(f"Erreur lors de l'exportation vers CSV: {str(e)}")
    
    def _do_json_export(self, file_path, config):
        """Effectue l'exportation vers JSON dans un thread séparé"""
        try:
            exporter = FormatExporter()
            return exporter.export_to_json(
                self.current_data, 
                file_path,
                encoding=config['encoding'],
                indent=config['indent'],
                as_array=config['as_array']
            )
        except Exception as e:
            raise Exception(f"Erreur lors de l'exportation vers JSON: {str(e)}")
    
    def _do_xml_export(self, file_path, config):
        """Effectue l'exportation vers XML dans un thread séparé"""
        try:
            exporter = FormatExporter()
            return exporter.export_to_xml(
                self.current_data, 
                file_path,
                encoding=config['encoding'],
                root_element=config['root_element'],
                item_element=config['item_element'],
                pretty_print=config['pretty_print']
            )
        except Exception as e:
            raise Exception(f"Erreur lors de l'exportation vers XML: {str(e)}")

    def _cell_changed(self, item):
        """Gestionnaire appelé lorsque le contenu d'une cellule est modifié"""
        # Récupérer les informations de la cellule modifiée
        row = item.row()
        column = item.column()
        new_value = item.text()
        
        # Mettre à jour les données en mémoire
        if self.current_data:
            self.current_data[row][self.headers[column]] = new_value
        
        # Afficher un message de confirmation
        self.status_bar.showMessage(f"Cellule ({row}, {column}) modifiée en '{new_value}'")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
