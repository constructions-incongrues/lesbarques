from bs4 import BeautifulSoup
import argparse
import html
import json
import re
import requests

DELIMITER = '***'


def paragraph_html(paragraph, italic_classes):
    """Texte du paragraphe, échappé, avec les spans italiques du Doc en <em>."""
    parts = []
    for span in paragraph.find_all('span', recursive=True):
        text = html.escape(span.get_text(), quote=False)
        if text.strip() and italic_classes & set(span.get('class', [])):
            text = f'<em>{text}</em>'
        parts.append(text)
    return ''.join(parts).strip()


def extract_texts(page):
    """
    Une entrée = les paragraphes entre deux `***` consécutifs, émise entourée de `***`
    pour que filter_texts (schedule.py) l'extraie sans bornes de longueur.
    Hors entrée : un texte par paragraphe, comme avant. Un `***` non refermé ne produit rien.
    """
    soup = BeautifulSoup(page, 'html.parser')
    # La classe italique change d'un Doc à l'autre : on la lit dans son CSS
    css = ' '.join(style.get_text() for style in soup.find_all('style'))
    italic_classes = set(re.findall(r'\.([\w-]+)\{[^}]*font-style:\s*italic', css))

    texts, entry, opened = [], [], False
    div = soup.find('div', {"id": "contents"})
    for paragraph in div.find_all('p', recursive=True) if div else []:
        # Un `***` peut être seul, collé en tête, ou au milieu d'un paragraphe
        for i, chunk in enumerate(paragraph_html(paragraph, italic_classes).split(DELIMITER)):
            if i > 0:  # un délimiteur précède ce morceau
                if opened and entry:
                    texts.append(DELIMITER + '<br><br>'.join(entry) + DELIMITER)
                entry, opened = [], True
            chunk = chunk.strip()
            if not chunk:
                continue
            if opened:
                entry.append(chunk)
            elif len(chunk) > 3:
                texts.append(chunk)
    return texts


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scraper pour extraire les textes d\'une page web.')
    parser.add_argument('urls', type=str, help='URLs des pages à scraper, séparées par des virgules')
    parser.add_argument('--insecure', help='Requêtes HTTP sécurisées', action='store_false')
    args = parser.parse_args()

    final_texts = []
    for url in args.urls.split(','):
        response = requests.get(url.strip(), verify=args.insecure, timeout=10)
        response.raise_for_status()
        final_texts.extend(extract_texts(response.content))

    print(json.dumps({"texts": final_texts}, ensure_ascii=False, indent=2))
