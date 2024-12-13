import json
import random

from jinja2 import Environment, FileSystemLoader

# Charger les données JSON
with open("../docs/results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sélectionner un texte, une image et un audio au hasard
text = random.choice(data["texts"])
image = random.choice(data["images"])
audio = random.choice(data["audios"])

# Configurer Jinja2 pour charger le modèle HTML
env = Environment(loader=FileSystemLoader("."), autoescape=True)
template = env.get_template("template.html")

# Rendre le modèle avec les données aléatoires
html_content = template.render(text=text, image=image, audio=audio)

# Enregistrer le contenu HTML dans un fichier
output_file = "../docs/index.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Le fichier HTML a été généré : {output_file}")
