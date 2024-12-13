import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime

# URL de la page à scraper
url = "https://loupuberto.fr/2650-2/"

# Créer un dossier unique basé sur la date et l'heure actuelles
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_folder = f"var/scrape/{timestamp}"
os.makedirs(output_folder, exist_ok=True)

# Envoyer une requête GET à la page
response = requests.get(url, verify=False)
response.raise_for_status()  # Vérifier que la requête a réussi

# Parser le contenu HTML de la page
soup = BeautifulSoup(response.content, 'html.parser')

# Extraire les textes
texts = []
paragraphs = soup.find_all('p')
for paragraph in paragraphs:
    text = paragraph.get_text()
    if text and text != '*':
        texts.append(text.strip ())

# Extraire les URLs des images
images = []
for img in soup.find_all('img'):
    img_url = img.get('src')
    if img_url:
        images.append(img_url)

# Extraire les URLs des fichiers audio
audios = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.mp3'):
        audios.append(href)

# Afficher les résultats
print("Textes extraits:")
print(texts)

print("\nImages extraites:")
for img in images:
    print(img)

print("\nAudios extraits:")
for audio in audios:
    print(audio)

# Exporter les résultats en JSON
results = {
    "texts": texts,
    "images": images,
    "audios": audios
}

json_path = os.path.join(output_folder, 'results.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\nLes résultats ont été exportés dans le fichier {json_path}")
