from bs4 import BeautifulSoup
from datetime import datetime
import argparse
import json
import os
import requests

# Télécharger les images et audios
def download_file(url, folder):
    try:
        local_filename = os.path.join(folder, url.split('/')[-1])
        if os.path.exists(local_filename):
            print(f"Le fichier {local_filename} existe déjà, téléchargement ignoré.")
            return local_filename
        with requests.get(url, stream=True, verify=args.insecure, timeout=600) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return local_filename
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du téléchargement du fichier {url}: {e}")
    except Exception as e:
        print(f"Erreur lors de l'enregistrement du fichier {url}: {e}")

# Timestamp pour identifier les résultats
timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Configurer les arguments de ligne de commande
parser = argparse.ArgumentParser(description='Scraper pour extraire les textes, images et audio d\'une page web.')
parser.add_argument('url', type=str, help='URL de la page à scraper')
parser.add_argument('--output-dir', type=str, help='Répertoire de sortie pour les résultats', default="docs")
parser.add_argument('--insecure', help='Requêtes HTTP sécurisées', action='store_false')
args = parser.parse_args()
print(args.insecure)

# URL de la page à scraper
url = args.url

# Créer un dossier de sortie pour les résultats
output_folder = args.output_dir
os.makedirs(output_folder, exist_ok=True)

# Envoyer une requête GET à la page
response = requests.get(url, verify=args.insecure   , timeout=10)
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
images_urls = []
for img in soup.find_all('img'):
    img_url = img.get('src').split('?')[0] if img.get('src') else None
    if img_url:
        images_urls.append(img_url)

# Extraire les URLs des fichiers audio
audios_urls = []
for link in soup.find_all('a'):
    href = link.get('href')
    if href and href.endswith('.mp3'):
        audios_urls.append(href)

# Afficher les résultats
print("Textes extraits:")
print(texts)

print("\nImages extraites:")
for img in images_urls:
    print(img)

print("\nAudios extraits:")
for audio in audios_urls:
    print(audio)

# Créer des sous-dossiers pour les images et les audios
images_folder = os.path.join(output_folder, 'images')
audios_folder = os.path.join(output_folder, 'audios')
os.makedirs(images_folder, exist_ok=True)
os.makedirs(audios_folder, exist_ok=True)

# Télécharger les images
images = []
for img_url in images_urls:
    images.append(download_file(img_url, images_folder).replace('docs/', ''))

# Télécharger les audios
audios = []
for audio_url in audios_urls:
    audios.append(download_file(audio_url, audios_folder).replace('docs/', ''))

# Exporter les résultats en JSON
results = {
    "timestamp": timestamp,
    "texts": texts,
    "images": images,
    "audios": audios
}

json_path = os.path.join(output_folder, 'manifest.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\nLes résultats ont été exportés dans le fichier {json_path}")