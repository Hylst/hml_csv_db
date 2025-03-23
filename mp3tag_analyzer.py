#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MP3Tag Analyzer
Auteur: Geoffroy Streit
Date: 23/03/2025
Description: Programme d'analyse de fichiers CSV générés par MP3tag et stockage en base SQLite
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from gui import MainWindow

def main():
    """Fonction principale du programme"""
    app = QApplication(sys.argv)
    app.setApplicationName("MP3Tag Analyzer")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
