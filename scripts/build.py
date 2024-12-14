import json
import random
import argparse
from jinja2 import Environment, FileSystemLoader

# Configurer les arguments de ligne de commande
parser = argparse.ArgumentParser(description='Générer un fichier HTML à partir d\'un modèle et de données JSON.')
parser.add_argument('--min-text-length', type=int, help='Longueur minimale du texte choisi', default=0)
parser.add_argument('--max-text-length', type=int, help='Longueur maximale du texte choisi', default=float('inf'))
args = parser.parse_args()

# Charger les données JSON
with open("./docs/manifest.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Filtrer les textes en fonction de la longueur minimale et maximale
filtered_texts = [text for text in data["texts"] if args.min_text_length <= len(text) <= args.max_text_length]

# Sélectionner un texte, une image et un audio au hasard
if filtered_texts:
    text = random.choice(filtered_texts)
else:
    print(f"Aucun texte ne correspond aux critères de longueur (min: {args.min_text_length}, max: {args.max_text_length} caractères).")
    exit(1)

image = random.choice(data["images"])
audio = random.choice(data["audios"])

# Configurer Jinja2 pour charger le modèle HTML
env = Environment(loader=FileSystemLoader("./templates"), autoescape=True)
template = env.get_template("index.html")

# Rendre le modèle avec les données aléatoires
html_content = template.render(text=text, image=image, audio=audio)

# Enregistrer le contenu HTML dans un fichier
output_file = "./docs/index.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Le fichier HTML a été généré : {output_file}")
