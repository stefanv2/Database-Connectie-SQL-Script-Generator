import sys
import subprocess
import json
import tempfile
import os
import random
import string
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QPushButton,
    QFormLayout, QVBoxLayout, QMessageBox, QComboBox, QGroupBox, QGraphicsOpacityEffect, QDialog
)
from PyQt6 import QtCore
from PyQt6.QtGui import QPixmap, QIcon
from cryptography.fernet import Fernet

def load_credentials():
    with open("key.key", "rb") as key_file:
        key = key_file.read()
    fernet = Fernet(key)
    with open("credentials.enc", "rb") as enc_file:
        encrypted_data = enc_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    credentials = json.loads(decrypted_data)
    return credentials

def generate_random_password():
    # Genereer 11 willekeurige tekens (letters en cijfers)
    chars = string.ascii_letters + string.digits
    password_core = ''.join(random.choices(chars, k=11))
    # Voeg een underscore toe aan het einde
    return password_core + "_"

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Connectie - SQL script generatie")
        # Stel het venstericoon in (zorg dat "icon.ico" beschikbaar is)
        self.setWindowIcon(QIcon("icon.ico"))
        self.loadFixedQueryMetadata()  # Laad de metadata voor vaste queries
        self.initUI()
    
    def loadFixedQueryMetadata(self):
        # Laad vaste query metadata uit een JSON-bestand
        self.fixed_query_metadata = {}
        metadata_file = "fixed_queries.json"
        if os.path.isfile(metadata_file):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    self.fixed_query_metadata = json.load(f)
            except Exception as e:
                QMessageBox.warning(self, "Waarschuwing", f"Kan {metadata_file} niet laden: {e}")
    
    def initUI(self):
        layout = QVBoxLayout()
        
        # Voeg een logo toe bovenaan
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")  # Zorg dat "logo.png" beschikbaar is
        pixmap = pixmap.scaledToWidth(200)
        logo_label.setPixmap(pixmap)
        logo_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Formulier voor connectie- en vaste query-instellingen
        form_layout = QFormLayout()
        
        # Database alias invoer
        self.db_alias_edit = QLineEdit()
        form_layout.addRow("Database alias:", self.db_alias_edit)
        
        # Invoer voor set linesize (optioneel)
        self.linesize_edit = QLineEdit()
        form_layout.addRow("Set linesize (optioneel):", self.linesize_edit)
        
        # Checkbox voor set heading off
        self.heading_checkbox = QCheckBox("Set heading off")
        form_layout.addRow(self.heading_checkbox)
        
        # Checkbox voor spool file opname
        self.spool_checkbox = QCheckBox("Spool file opnemen")
        self.spool_checkbox.stateChanged.connect(self.toggleSpoolFields)
        form_layout.addRow(self.spool_checkbox)
        
        # Invoer voor spool directory (default "c:\temp")
        self.spool_dir_edit = QLineEdit("c:\\temp")
        self.spool_dir_edit.setEnabled(False)
        form_layout.addRow("Spool directory:", self.spool_dir_edit)
        
        # Invoer voor spool file naam (default "spool.log")
        self.spool_name_edit = QLineEdit("spool.log")
        self.spool_name_edit.setEnabled(False)
        form_layout.addRow("Spool file naam:", self.spool_name_edit)
        
        # Checkbox voor extra omgevingsinstellingen (NLS_LANG en chcp)
        self.extra_checkbox = QCheckBox("Stel NLS_LANG en chcp 1252 in")
        form_layout.addRow(self.extra_checkbox)
        
        # Checkbox voor direct uitvoeren van een extra script
        self.direct_script_checkbox = QCheckBox("Voer script direct uit")
        self.direct_script_checkbox.stateChanged.connect(self.toggleDirectScriptField)
        form_layout.addRow(self.direct_script_checkbox)
        
        # Invulveld voor het pad naar het script dat direct uitgevoerd moet worden
        self.direct_script_edit = QLineEdit()
        self.direct_script_edit.setPlaceholderText("Bijv. C:\\temp\\myscript.sql")
        self.direct_script_edit.setEnabled(False)
        form_layout.addRow("Script pad:", self.direct_script_edit)
        
        # Nieuwe sectie: Vaste query's vanuit de "sql" map
        self.fixed_query_combo = QComboBox()
        sql_folder = "sql"
        if os.path.isdir(sql_folder):
            files = [f for f in os.listdir(sql_folder) if f.lower().endswith(".sql")]
            self.fixed_query_combo.addItems(files)
        else:
            self.fixed_query_combo.addItem("Geen SQL folder gevonden")
        form_layout.addRow("Kies vaste query:", self.fixed_query_combo)
        
        # Tekstvak voor uitleg van de vaste query
        self.fixed_query_explanation = QLabel("Beschrijving: Geen beschrijving beschikbaar.")
        self.fixed_query_explanation.setWordWrap(True)
        form_layout.addRow("Beschrijving:", self.fixed_query_explanation)
        
        # Update uitleg bij selectie vaste query
        self.fixed_query_combo.currentTextChanged.connect(self.updateFixedQueryExplanation)
        
        layout.addLayout(form_layout)
        
        # Voeg gebruikersbeheer-sectie toe
        self.add_user_management_section(layout)
        
        # Knop om het SQL-script te genereren en SQL*Plus te starten (connectie)
        self.connect_button = QPushButton("Genereer SQL script en verbind")
        self.connect_button.clicked.connect(self.connect_with_sql_script)
        layout.addWidget(self.connect_button)
        
        # Knop om de vaste query direct uit te voeren
        self.fixed_query_button = QPushButton("Voer vaste query uit")
        self.fixed_query_button.clicked.connect(self.run_fixed_query)
        layout.addWidget(self.fixed_query_button)
        
        # Statuslabel (wachtwoord wordt hier niet getoond)
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)
        
        # Nieuwe toevoeging: watermerk onderaan
        bottom_image_label = QLabel()
        bottom_pixmap = QPixmap("bottom.png")  # Zorg dat "bottom.png" beschikbaar is
        bottom_pixmap = bottom_pixmap.scaledToWidth(100)
        bottom_image_label.setPixmap(bottom_pixmap)
        bottom_image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.8)
        bottom_image_label.setGraphicsEffect(opacity_effect)
        layout.addWidget(bottom_image_label)
        
        self.setLayout(layout)
    
    def add_user_management_section(self, parent_layout):
        # Voeg een aparte sectie toe voor gebruikersbeheer
        user_group = QGroupBox("Gebruikersbeheer")
        user_layout = QFormLayout()
        self.target_username_edit = QLineEdit()
        user_layout.addRow("Doel username:", self.target_username_edit)
        self.unlock_checkbox = QCheckBox("Account unlocken")
        user_layout.addRow(self.unlock_checkbox)
        self.change_password_button = QPushButton("Wijzig gebruikerswachtwoord")
        self.change_password_button.clicked.connect(self.change_user_password)
        user_layout.addRow(self.change_password_button)
        user_group.setLayout(user_layout)
        parent_layout.addWidget(user_group)
    
    def toggleSpoolFields(self):
        enabled = self.spool_checkbox.isChecked()
        self.spool_dir_edit.setEnabled(enabled)
        self.spool_name_edit.setEnabled(enabled)
    
    def toggleDirectScriptField(self):
        enabled = self.direct_script_checkbox.isChecked()
        self.direct_script_edit.setEnabled(enabled)
    
    def updateFixedQueryExplanation(self, filename):
        desc = self.fixed_query_metadata.get(filename, "Geen beschrijving beschikbaar.")
        self.fixed_query_explanation.setText(desc)
    
    def connect_with_sql_script(self):
        db_alias = self.db_alias_edit.text().strip()
        if not db_alias:
            QMessageBox.critical(self, "Fout", "Vul een database alias in.")
            return
        try:
            credentials = load_credentials()
            user = credentials["username"]
            password = credentials["password"]
            conn_string = f"{user}/{password}@{db_alias}"
            conn_info = f"{user}@{db_alias}"
            self.status_label.setText(f"Verbinden met: {conn_info}")
            
            temp_sql = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.sql')
            if self.spool_checkbox.isChecked():
                spool_dir = self.spool_dir_edit.text().strip()
                spool_name = self.spool_name_edit.text().strip()
                if spool_dir and spool_name:
                    if not os.path.isdir(spool_dir):
                        QMessageBox.critical(self, "Fout", f"De map '{spool_dir}' bestaat niet.")
                        temp_sql.close()
                        os.unlink(temp_sql.name)
                        return
                    spool_full = os.path.join(spool_dir, spool_name)
                    temp_sql.write(f"spool {spool_full}\n")
                else:
                    QMessageBox.critical(self, "Fout", "Geef zowel een spool directory als een spool file naam op.")
                    temp_sql.close()
                    os.unlink(temp_sql.name)
                    return
            linesize = self.linesize_edit.text().strip()
            if linesize:
                temp_sql.write(f"set linesize {linesize};\n")
            if self.heading_checkbox.isChecked():
                temp_sql.write("set heading off;\n")
            if self.direct_script_checkbox.isChecked():
                script_path = self.direct_script_edit.text().strip()
                if not script_path or not os.path.isfile(script_path):
                    QMessageBox.critical(self, "Fout", "Het opgegeven script bestaat niet.")
                    temp_sql.close()
                    os.unlink(temp_sql.name)
                    return
                temp_sql.write(f"@{script_path}\n")
            temp_sql.close()
            if self.extra_checkbox.isChecked():
                temp_bat = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat')
                temp_bat.write(f"""@echo off
set NLS_LANG=DUTCH_THE NETHERLANDS.AL32UTF8
chcp 1252
sqlplus {conn_string} @{temp_sql.name}
del "%~f0"
""")
                temp_bat.close()
                subprocess.Popen([temp_bat.name],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["sqlplus", conn_string, "@" + temp_sql.name],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            QMessageBox.critical(self, "Verbindingsfout", f"Er is een fout opgetreden: {e}")
    
    def run_fixed_query(self):
        fixed_query_file = self.fixed_query_combo.currentText()
        sql_folder = "sql"
        full_query_path = os.path.join(sql_folder, fixed_query_file)
        if not os.path.isfile(full_query_path):
            QMessageBox.critical(self, "Fout", "Het geselecteerde querybestand bestaat niet.")
            return
        db_alias = self.db_alias_edit.text().strip()
        if not db_alias:
            QMessageBox.critical(self, "Fout", "Vul een database alias in.")
            return
        try:
            credentials = load_credentials()
            user = credentials["username"]
            password = credentials["password"]
            conn_string = f"{user}/{password}@{db_alias}"
            conn_info = f"{user}@{db_alias}"
            self.status_label.setText(f"Verbinden met: {conn_info}")
            
            temp_sql = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.sql')
            if self.spool_checkbox.isChecked():
                spool_dir = self.spool_dir_edit.text().strip()
                spool_name = self.spool_name_edit.text().strip()
                if spool_dir and spool_name:
                    if not os.path.isdir(spool_dir):
                        QMessageBox.critical(self, "Fout", f"De map '{spool_dir}' bestaat niet.")
                        temp_sql.close()
                        os.unlink(temp_sql.name)
                        return
                    spool_full = os.path.join(spool_dir, spool_name)
                    temp_sql.write(f"spool {spool_full}\n")
                else:
                    QMessageBox.critical(self, "Fout", "Geef zowel een spool directory als een spool file naam op.")
                    temp_sql.close()
                    os.unlink(temp_sql.name)
                    return
            linesize = self.linesize_edit.text().strip()
            if linesize:
                temp_sql.write(f"set linesize {linesize};\n")
            if self.heading_checkbox.isChecked():
                temp_sql.write("set heading off;\n")
            temp_sql.write(f"@{full_query_path}\n")
            temp_sql.close()
            if self.extra_checkbox.isChecked():
                temp_bat = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.bat')
                temp_bat.write(f"""@echo off
set NLS_LANG=DUTCH_THE NETHERLANDS.AL32UTF8
chcp 1252
sqlplus {conn_string} @{temp_sql.name}
del "%~f0"
""")
                temp_bat.close()
                subprocess.Popen([temp_bat.name],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                subprocess.Popen(["sqlplus", conn_string, "@" + temp_sql.name],
                                 creationflags=subprocess.CREATE_NEW_CONSOLE)
        except Exception as e:
            QMessageBox.critical(self, "Verbindingsfout", f"Er is een fout opgetreden: {e}")
    
    def show_new_password_dialog(self, target_user, new_password):
        # Kopieer het nieuwe wachtwoord naar het klembord
        clipboard = QApplication.clipboard()
        clipboard.setText(new_password)
        
        # Maak een dialoogvenster om het nieuwe wachtwoord te tonen
        dialog = QDialog(self)
        dialog.setWindowTitle("Nieuw Wachtwoord")
        layout = QVBoxLayout(dialog)
        
        info_label = QLabel(f"Wachtwoord voor {target_user} gewijzigd:")
        layout.addWidget(info_label)
        
        password_edit = QLineEdit(new_password)
        password_edit.setReadOnly(True)
        layout.addWidget(password_edit)
        
        copy_button = QPushButton("Kopieer wachtwoord")
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(new_password))
        layout.addWidget(copy_button)
        
        close_button = QPushButton("Sluiten")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def change_user_password(self):
        target_user = self.target_username_edit.text().strip()
        if not target_user:
            QMessageBox.critical(self, "Fout", "Vul de gebruikersnaam in waarvoor je het wachtwoord wilt wijzigen.")
            return
        new_password = generate_random_password()
        
        temp_sql = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.sql')
        temp_sql.write(f"ALTER USER {target_user} IDENTIFIED BY {new_password};\n")
        if self.unlock_checkbox.isChecked():
            temp_sql.write(f"ALTER USER {target_user} ACCOUNT UNLOCK;\n")
        temp_sql.close()
        
        db_alias = self.db_alias_edit.text().strip()
        if not db_alias:
            QMessageBox.critical(self, "Fout", "Vul de database alias in voor de connectie.")
            return
        try:
            credentials = load_credentials()
            admin_user = credentials["username"]
            admin_password = credentials["password"]
            conn_string = f"{admin_user}/{admin_password}@{db_alias}"
            subprocess.Popen(["sqlplus", conn_string, "@" + temp_sql.name],
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.show_new_password_dialog(target_user, new_password)
        except Exception as e:
            QMessageBox.critical(self, "Fout", f"Er is een fout opgetreden: {e}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
