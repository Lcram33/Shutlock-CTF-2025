import sqlite3
import zlib
import os


# Connexion à la base de données SQLite
conn = sqlite3.connect("bigTopDataDB.-286538739")
cursor = conn.cursor()

# Création d'un dossier pour stocker les messages HTML
output_dir = "messages_html"
os.makedirs(output_dir, exist_ok=True)

# Récupération des messages compressés
cursor.execute("SELECT zipped_message_proto FROM item_messages")
rows = cursor.fetchall()

for i, row in enumerate(rows):
    if not row or not row[0]:
        continue

    compressed_data = row[0]
    i += 1

    try:
        # Retirer le premier octet s'il ne correspond pas à une entête zlib valide
        if compressed_data[:2] != b'\x78\x9c':  # zlib standard header
            compressed_data = compressed_data[1:]

        decompressed_data = zlib.decompress(compressed_data)

        # Supprimer les caractères non-ASCII
        cleaned_data = decompressed_data.decode("utf-8", errors="ignore")
        cleaned_data_ascii = ''.join(x for x in cleaned_data if 32 <= ord(x) <= 126)

        # Sauvegarde dans un fichier HTML
        output_path = os.path.join(output_dir, f"message_{i}.html")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_data_ascii)

        print(f"Message {i} sauvegardé dans {output_path}")

    except Exception as e:
        print(f"Erreur sur le message {i} : {e}")
