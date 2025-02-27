import pandas as pd
import sqlite3

# Demander à l'utilisateur le nom du fichier CSV et le nom de la table
csv_file = input("Entrez le nom du fichier CSV (avec l'extension .csv) : ")
table_name = input("Entrez le nom de la table SQLite : ")

# Connexion à la base de données SQLite (elle sera créée si elle n'existe pas)
conn = sqlite3.connect('bdd_festiv.db')

# Chargement du fichier CSV dans un DataFrame pandas
df = pd.read_csv(csv_file)

# Écriture des données dans une table SQLite avec le nom spécifié par l'utilisateur
df.to_sql(table_name, conn, if_exists='replace', index=False)

# Fermeture de la connexion
conn.close()

print(f"Les données du fichier {csv_file} ont été importées dans la table '{table_name}' de la base de données SQLite.")