import requests
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import argparse

# Configurer les arguments de ligne de commande
parser = argparse.ArgumentParser(description='Scraper pour extraire les textes, images et audio d\'une page web.')
parser.add_argument('url', type=str, help='URL de la page à scraper')
parser.add_argument('--output-dir', type=str, help='Répertoire de sortie pour les résultats', default=None)
args = parser.parse_args()

# URL de la page à scraper
url = args.url

# Timestamp pour identifier les résultats
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Créer un dossier de sortie pour les résultats
output_folder = args.output_dir
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
        texts.append(text.strip())

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
    "timestamp": timestamp,
    "texts": texts,
    "images": images,
    "audios": audios
}

json_path = os.path.join(output_folder, 'results.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\nLes résultats ont été exportés dans le fichier {json_path}")

# Télécharger les images et audios
def download_file(url, folder):
    try:
        local_filename = os.path.join(folder, url.split('/')[-1])
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier {url}: {e}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier {url}: {e}")

# Créer des sous-dossiers pour les images et les audios
images_folder = os.path.join(output_folder, 'images')
audios_folder = os.path.join(output_folder, 'audios')
os.makedirs(images_folder, exist_ok=True)
os.makedirs(audios_folder, exist_ok=True)

# Télécharger les images
for img_url in images:
    download_file(img_url, images_folder)

# Télécharger les audios
for audio_url in audios:
    download_file(audio_url, audios_folder)
