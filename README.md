\# Database Connectie - SQL Script Generator


<p align="center">
<img src="logo.png" alt="BTOP" width="300" height="300"/>  
</p>


Een Python GUI-tool (PyQt6) voor het snel opzetten van een Oracle databaseconnectie, uitvoeren van vaste SQL-query's en het genereren van uitvoerbare SQL-scripts met opties zoals spool, linesize, heading en gebruikersbeheer.



\## 🎯 Doel



Deze tool is bedoeld voor DBA’s of ontwikkelaars die snel:

\- een connectie willen leggen met een Oracle database,

\- een vaste SQL-query willen uitvoeren,

\- of gebruikersaccounts willen beheren via een GUI.



Ideaal voor herbruikbare SQL-scripts, auditqueries, en ad-hoc connecties zonder handmatig scripten.



---



\## 🖥️ Functionaliteiten



\- 🔐 \*\*Credential Management\*\* (via versleuteld bestand)

\- 💾 \*\*Spoolopties\*\* (inclusief pad \& bestandsnaam)

\- 🧾 \*\*Linesize en heading configuratie\*\*

\- 📜 \*\*Direct script uitvoeren (.sql)\*\*

\- 📂 \*\*Vaste query’s laden uit `sql/` map + metadata (JSON)\*\*

\- 👤 \*\*Gebruikersbeheer (unlock + password reset met random generator)\*\*

\- 🎨 \*\*GUI met logo en beschrijvingen\*\*



---



\## 🚀 Installatie



1\. Zorg dat Python 3.10+ is geïnstalleerd

2\. Installeer dependencies:



```bash


pip install pyqt6 cryptography


Clone of kopieer dit project, en plaats het in een folder met:

key.key — de encryptiesleutel

credentials.enc — versleutelde Oracle login (JSON)

sql/ — folder met .sql bestanden

fixed_queries.json — metadata voor de vaste query’s

logo.png, icon.ico, bottom.png — optioneel voor branding

Start de applicatie:


python start_sql3.py



sql-generator/
├── start_sql3.py               # De hoofdapplicatie (GUI)
├── versleutel.py               # Script om credentials te versleutelen
├── credentials.json            # (tijdelijk) open JSON met login
├── credentials.enc             # Versleutelde login info
├── key.key                     # AES-sleutel
├── sql/                        # Map met herbruikbare .sql-query's
├── fixed_queries.json          # Metadata voor query-uitleg
├── icon.ico / logo.png         # Optionele branding
└── README.md


🔐 Credential versleutelen
Je gebruikt het script versleutel.py om je credentials.json veilig om te zetten naar een versleuteld bestand (credentials.enc).

Stap 1: Genereer de sleutel (eenmalig)
from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("key.key", "wb") as f:
    f.write(key)

Stap 2: Maak een credentials.json
{
  "username": "scott",
  "password": "tiger"
}
Stap 3: Versleutel met versleutel.py
python
Kopiëren
Bewerken
from cryptography.fernet import Fernet

# Lees de sleutel in
with open("key.key", "rb") as key_file:
    key = key_file.read()
fernet = Fernet(key)

# Lees de originele JSON-data
with open("credentials.json", "rb") as file:
    original_data = file.read()

# Versleutel de data
encrypted_data = fernet.encrypt(original_data)

# Sla de versleutelde data op
with open("credentials.enc", "wb") as enc_file:
    enc_file.write(encrypted_data)

print("Credentials versleuteld en opgeslagen in credentials.enc")
Je kunt daarna credentials.json verwijderen.


▶️ Starten van de tool
Zorg dat je je projectstructuur goed hebt ingericht en voer uit:

python start_sql3.py
🧠 Werking vaste query’s
Alle .sql bestanden in de sql/ map worden automatisch geladen

De uitleg per bestand staat in fixed_queries.json:

{
  "gebruikers_overzicht.sql": "Geeft alle actieve gebruikers terug met rollen en status.",
  "tablespace_check.sql": "Overzicht van beschikbare en gebruikte ruimte per tablespace."
}
Deze worden weergegeven in de GUI bij selectie.

🧪 Extra opties in GUI
Spool inschakelen: geef directory en bestandsnaam op

Direct script uitvoeren: laad een bestaand SQL-bestand

NLS_LANG + chcp 1252: vink aan voor internationale tekens

Gebruikersbeheer:

Vul username in

Vink aan om te unlocken

Klik “Wachtwoord wijzigen” → random wachtwoord + dialoog


