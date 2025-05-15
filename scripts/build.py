import json
import random
import argparse
from jinja2 import Environment, FileSystemLoader

# Configurer les arguments de ligne de commande
parser = argparse.ArgumentParser(description='Générer un fichier HTML à partir d\'un modèle et de données JSON.')
parser.add_argument('--min-text-length', type=int, help='Longueur minimale du texte choisi', default=0)
parser.add_argument('--max-text-length', type=int, help='Longueur maximale du texte choisi', default=float('inf'))
parser.add_argument('--delimiter', type=str, help='Délimiteur pour extraire une partie du texte (même valeur pour début et fin)', default='***')
args = parser.parse_args()

# Charger les données JSON
with open("./docs/manifest.json", "r", encoding="utf-8") as f:
    data = json.load(f)

texts = data["texts"]
filtered_texts = []

# Traiter chaque texte individuellement
for text in texts:
    # Chercher les positions du délimiteur
    delimiter_positions = [pos for pos in range(len(text)) if text.startswith(args.delimiter, pos)]

    # Si le texte contient au moins deux délimiteurs, extraire la portion entre les deux premiers
    if len(delimiter_positions) >= 2:
        start_pos = delimiter_positions[0] + len(args.delimiter)
        end_pos = delimiter_positions[1]
        extracted_text = text[start_pos:end_pos]
        filtered_texts.append(extracted_text)
    # Sinon, appliquer les règles de longueur min/max
    elif args.min_text_length <= len(text) <= args.max_text_length:
        filtered_texts.append(text)

# Sélectionner un texte, une image et un audio au hasard
if filtered_texts:
    # trunk-ignore(bandit/B311)
    text = random.choice(filtered_texts)
else:
    print("Aucun texte ne correspond aux critères (délimiteur ou longueur).")
    exit(1)

# trunk-ignore(bandit/B311)
image = random.choice(data["images"])
# trunk-ignore(bandit/B311)
audio = random.choice(data["audios"])

# Afficher les éléments choisis
print("\n=== ÉLÉMENTS SÉLECTIONNÉS ===")
print(f"TEXTE:\n{text}\n")
print(f"IMAGE: {image}")
print(f"AUDIO: {audio}")
print("===========================\n")

# Configurer Jinja2 pour charger le modèle HTML
env = Environment(loader=FileSystemLoader("./templates"), autoescape=True)
template = env.get_template("index.html")
template = env.get_template("index.html")

# Rendre le modèle avec les données aléatoires
html_content = template.render(text=text, image=image, audio=audio)

# Enregistrer le contenu HTML dans un fichier
output_file = "./docs/index.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Le fichier HTML a été généré : {output_file}")