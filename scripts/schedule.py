import json
import random
import os
import datetime
import argparse
from jinja2 import Environment, FileSystemLoader

def filter_texts(texts, min_text_length=0, max_text_length=float('inf'), delimiter='***'):
    """
    Filtre les textes selon les critères de délimiteur et de longueur
    """
    filtered_texts = []

    # Traiter chaque texte individuellement
    for text in texts:
        # Chercher les positions du délimiteur
        delimiter_positions = [pos for pos in range(len(text)) if text.startswith(delimiter, pos)]

        # Si le texte contient au moins deux délimiteurs, extraire la portion entre les deux premiers
        if len(delimiter_positions) >= 2:
            start_pos = delimiter_positions[0] + len(delimiter)
            end_pos = delimiter_positions[1]
            extracted_text = text[start_pos:end_pos]
            filtered_texts.append(extracted_text)
        # Sinon, appliquer les règles de longueur min/max
        elif min_text_length <= len(text) <= max_text_length:
            filtered_texts.append(text)

    return filtered_texts


def get_current_day_index(start_date, cycle_length=30, today=None):
    """
    Calcule l'index du jour actuel depuis la date de début du cycle.
    Retourne un tuple (index_dans_cycle, numéro_de_cycle)
    """
    if today is None:
        today = datetime.datetime.now().date()
    else:
        if isinstance(today, str):
            today = datetime.datetime.strptime(today, "%Y-%m-%d").date()

    start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    days_passed = (today - start).days

    if days_passed < 0:
        return 0, 0  # Avant le démarrage du cycle

    cycle_number = days_passed // cycle_length + 1  # Les cycles commencent à 1
    day_index = days_passed % cycle_length

    return day_index, cycle_number

def load_or_create_schedule(manifest_path, schedule_path, min_text_length=0, max_text_length=float('inf'), delimiter='***', cycle_length=30):
    """
    Charge le planning existant ou en crée un nouveau s'il n'existe pas
    """
    # Vérifier si le fichier de planning existe
    if os.path.exists(schedule_path):
        with open(schedule_path, "r", encoding="utf-8") as f:
            schedule_data = json.load(f)
            # Vérifier si le cycle_length a changé
            if 'cycle_length' not in schedule_data or schedule_data['cycle_length'] != cycle_length:
                print(f"La longueur du cycle a changé de {schedule_data.get('cycle_length', 'non défini')} à {cycle_length} jours.")
                schedule_data['cycle_length'] = cycle_length
                # Enregistrer le planning mis à jour
                with open(schedule_path, "w", encoding="utf-8") as f:
                    json.dump(schedule_data, f, ensure_ascii=False, indent=4)
            return schedule_data

    # Si non, créer un nouveau planning
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Filtrer les textes selon les critères
    filtered_texts = filter_texts(manifest["texts"], min_text_length, max_text_length, delimiter)

    if not filtered_texts:
        print("Aucun texte ne correspond aux critères (délimiteur ou longueur).")
        return None

    # Créer une liste de toutes les combinaisons possibles de texte/image/audio
    entries = []
    used_texts = set()  # Pour éviter les doublons de texte

    # D'abord essayer de créer des entrées avec des textes uniques
    for text in filtered_texts:
        if text not in used_texts:
            entry = {
                "text": text,
                "image": random.choice(manifest["images"]),
                "audio": random.choice(manifest["audios"])
            }
            entries.append(entry)
            used_texts.add(text)

    # Vérifier combien d'entrées uniques nous avons
    print(f"Créé {len(entries)} entrées avec des textes uniques.")

    # Si nous avons moins d'entrées que la longueur du cycle et qu'il n'y a plus de textes uniques disponibles
    if len(entries) < cycle_length and len(entries) == len(filtered_texts):
        print(f"Attention: Seulement {len(filtered_texts)} textes uniques disponibles, certains textes seront répétés pour atteindre {cycle_length} entrées.")

        # Calculer combien d'entrées supplémentaires sont nécessaires
        additional_needed = cycle_length - len(entries)

        # Réutiliser des textes en évitant les doublons d'image/audio autant que possible
        for _ in range(additional_needed):
            # Choisir un texte au hasard
            text = random.choice(filtered_texts)

            # Créer une nouvelle entrée avec ce texte mais des image/audio différents si possible
            used_combinations = [(e["image"], e["audio"]) for e in entries if e["text"] == text]
            possible_images = manifest["images"]
            possible_audios = manifest["audios"]

            # Essayer de trouver une combinaison image/audio pas encore utilisée avec ce texte
            found_unique = False
            max_attempts = 10  # Limiter le nombre de tentatives

            for _ in range(max_attempts):
                img = random.choice(possible_images)
                aud = random.choice(possible_audios)

                if (img, aud) not in used_combinations:
                    entry = {"text": text, "image": img, "audio": aud}
                    entries.append(entry)
                    found_unique = True
                    break

            # Si on n'a pas trouvé de combinaison unique, en prendre une au hasard
            if not found_unique:
                entry = {
                    "text": text,
                    "image": random.choice(manifest["images"]),
                    "audio": random.choice(manifest["audios"])
                }
                entries.append(entry)

    # Si nous avons plus d'entrées que la longueur du cycle, n'en prendre que cycle_length
    if len(entries) > cycle_length:
        entries = random.sample(entries, cycle_length)

    # Mélanger les entrées
    random.shuffle(entries)

    # Créer le planning avec la date de début à aujourd'hui
    today = datetime.datetime.now().date().strftime("%Y-%m-%d")
    schedule_data = {
        "cycle_start_date": today,
        "cycle_length": cycle_length,
        "entries": entries,
        "cycles": {}  # Pour stocker l'historique des cycles
    }

    # Enregistrer le planning
    with open(schedule_path, "w", encoding="utf-8") as f:
        json.dump(schedule_data, f, ensure_ascii=False, indent=4)

    return schedule_data

def generate_today_content(schedule_data, output_file, force_day=None):
    """
    Génère le contenu pour aujourd'hui en fonction du planning
    """
    start_date = schedule_data["cycle_start_date"]
    cycle_length = schedule_data.get("cycle_length", 30)  # Par défaut 30 jours si non défini

    # Si force_day est défini, utiliser cette valeur plutôt que la date du jour
    if force_day is not None:
        day_index, cycle_number = force_day, 1  # On présume le cycle 1 pour un jour forcé
    else:
        day_index, cycle_number = get_current_day_index(start_date, cycle_length)

    print(f"Jour {day_index+1}/{cycle_length} du cycle {cycle_number}")

    # Si nous commençons un nouveau cycle (et ce n'est pas le premier jour du premier cycle)
    if day_index == 0 and cycle_number > 1 and not force_day:
        # Sauvegarder l'ancien cycle
        if str(cycle_number-1) not in schedule_data["cycles"]:
            schedule_data["cycles"][str(cycle_number-1)] = schedule_data["entries"].copy()

        # Mélanger à nouveau les entrées pour le nouveau cycle
        random.shuffle(schedule_data["entries"])

        # Mettre à jour la date de début du cycle
        schedule_data["cycle_start_date"] = datetime.datetime.now().date().strftime("%Y-%m-%d")

        # Enregistrer le planning mis à jour
        with open(schedule_path, "w", encoding="utf-8") as f:
            json.dump(schedule_data, f, ensure_ascii=False, indent=4)

    # Obtenir l'entrée du jour
    if day_index < len(schedule_data["entries"]):
        today_entry = schedule_data["entries"][day_index]

        # Générer le HTML avec le template
        env = Environment(loader=FileSystemLoader("./templates"), autoescape=True)
        template = env.get_template("index.html")

        # Ajouter des métadonnées sur le cycle et le jour
        today_entry["cycle"] = cycle_number
        today_entry["day"] = day_index + 1
        today_entry["total_days"] = len(schedule_data["entries"])

        html_content = template.render(**today_entry)

        # Enregistrer le contenu HTML dans un fichier
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"\n=== CONTENU DU JOUR {day_index+1} ===")
        print(f"TEXTE:\n{today_entry['text']}\n")
        print(f"IMAGE: {today_entry['image']}")
        print(f"AUDIO: {today_entry['audio']}")
        print("===========================\n")

        print(f"Le fichier HTML a été généré : {output_file}")
    else:
        print(f"Erreur: Jour {day_index+1} hors des limites du planning")

if __name__ == "__main__":
    # Configurer les arguments de ligne de commande
    parser = argparse.ArgumentParser(description='Générer du contenu quotidien selon un planning prédéfini.')
    parser.add_argument('--force-day', type=int, help='Forcer un jour spécifique (0-N)', default=None)
    parser.add_argument('--reset', action='store_true', help='Réinitialiser le planning')
    parser.add_argument('--min-text-length', type=int, help='Longueur minimale du texte choisi', default=0)
    parser.add_argument('--max-text-length', type=int, help='Longueur maximale du texte choisi', default=float('inf'))
    parser.add_argument('--delimiter', type=str, help='Délimiteur pour extraire une partie du texte', default='***')
    parser.add_argument('--cycle-length', type=int, help='Nombre de jours dans un cycle', default=30)
    args = parser.parse_args()

    # Chemins des fichiers
    manifest_path = "./docs/manifest.json"
    schedule_path = "./docs/schedule.json"
    output_file = "./docs/index.html"

    # Réinitialiser le planning si demandé
    if args.reset and os.path.exists(schedule_path):
        os.remove(schedule_path)
        print("Planning réinitialisé.")

    # Charger ou créer le planning
    schedule_data = load_or_create_schedule(
        manifest_path,
        schedule_path,
        args.min_text_length,
        args.max_text_length,
        args.delimiter,
        args.cycle_length
    )

    # Générer le contenu du jour
    if schedule_data:
        generate_today_content(schedule_data, output_file, args.force_day)
    else:
        print("Impossible de générer le contenu: aucun texte ne correspond aux critères.")

