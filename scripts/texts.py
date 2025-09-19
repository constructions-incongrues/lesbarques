from bs4 import BeautifulSoup
import argparse
import json
import os
import requests

# Configurer les arguments de ligne de commande
parser = argparse.ArgumentParser(description='Scraper pour extraire les textes d\'une page web.')
parser.add_argument('urls', type=str, help='URLs des pages à scraper, séparées par des virgules')
parser.add_argument('--output-dir', type=str, help='Répertoire de sortie pour les résultats', default="docs")
parser.add_argument('--insecure', help='Requêtes HTTP sécurisées', action='store_false')
args = parser.parse_args()

# Liste des URLs à scraper
urls = args.urls.split(',')

# Créer un dossier de sortie pour les résultats
output_folder = args.output_dir
os.makedirs(output_folder, exist_ok=True)

# Initialiser les résultats finaux
final_texts = []

for url in urls:
    # Envoyer une requête GET à la page
    response = requests.get(url.strip(), verify=args.insecure, timeout=10)
    response.raise_for_status()  # Vérifier que la requête a réussi

    # Parser le contenu HTML de la page
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extraire les textes
    texts = []
    div = soup.find('div', {"id": "contents"})
    if div:
        paragraphs = div.find_all('p', recursive=True)
        for paragraph in paragraphs:
            spans = paragraph.find_all('span', recursive=True)
            text_parts = []
            for span in spans:
                text_parts += span.get_text()
            text = ''.join(text_parts)
            if text and len(text) > 3:
                texts.append(text.strip())

    # Ajouter les résultats à la liste finale
    final_texts.extend(texts)

# Exporter les résultats en JSON
results = {
    "texts": final_texts
}

# Afficher les résultats au format JSON dans la console
print(json.dumps(results, ensure_ascii=False, indent=2))
