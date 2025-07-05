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