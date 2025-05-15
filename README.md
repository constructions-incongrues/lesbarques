# Script pour la génération automatique quotidienne de contenu

Ce script permet de mettre en place un système qui:
1. Organise aléatoirement une liste d'entrées (textes, images, sons) une fois au début d'un cycle
2. Publie une entrée par jour selon cet ordre prédéfini
3. Après 120 jours (fin du cycle), réorganise aléatoirement les entrées et recommence

## Installation

Assurez-vous d'avoir Python 3.6+ installé et les dépendances requises:

```bash
pip install jinja2 beautifulsoup4 requests
```

## Fichiers du système

- `schedule.py` - Le nouveau script qui gère la planification du contenu
- `scripts/scrape.py` - Script existant pour récupérer du contenu (inchangé)
- `docs/manifest.json` - Fichier contenant toutes les ressources disponibles
- `docs/schedule.json` - Nouveau fichier qui stocke la planification des publications
- `docs/index.html` - Fichier généré contenant l'entrée du jour

## Mode d'emploi

### 1. Récupérer du contenu (si nécessaire)

Utilisez le script `scrape.py` comme auparavant pour récupérer du contenu:

```bash
python scripts/scrape.py URL1,URL2,URL3 --output-dir docs
```

### 2. Générer la planification initiale et le contenu du jour

```bash
python schedule.py
```

Ce script:
- Crée un nouveau fichier `schedule.json` lors de la première exécution
- Organise aléatoirement les entrées (textes, images, sons)
- Génère le contenu du jour dans `index.html`

### 3. Automatisation quotidienne

Configurez une tâche cron pour exécuter le script tous les jours:

```bash
# Exécuter tous les jours à minuit
0 0 * * * cd /chemin/vers/votre/projet && python schedule.py
```

### Options supplémentaires

```bash
# Réinitialiser la planification (crée un nouveau cycle aléatoire)
python schedule.py --reset

# Générer le contenu d'un jour spécifique
python schedule.py --force-day 15

# Filtrer les textes par longueur
python schedule.py --min-text-length 100 --max-text-length 500

# Utiliser des délimiteurs pour extraire des portions de texte
python schedule.py --delimiter "***"

# Définir une longueur de cycle personnalisée (nombre de jours par cycle)
python schedule.py --cycle-length 60
```

## Fonctionnalités de filtrage des textes

Tout comme le script `build.py` original, le nouveau script `schedule.py` permet de filtrer les textes de deux façons:

1. **Par délimiteur** - Extrait du texte entre deux délimiteurs identiques:
   ```
   ***Ceci est le texte qui sera extrait.***
   ```

2. **Par longueur** - Sélectionne les textes dont la longueur est comprise entre un minimum et un maximum:
   ```bash
   python schedule.py --min-text-length 100 --max-text-length 500
   ```

Ces options permettent de contrôler précisément les textes qui seront inclus dans la planification. Si un texte contient le délimiteur spécifié, seule la partie entre les délimiteurs sera utilisée. Sinon, le texte entier sera utilisé s'il respecte les contraintes de longueur.

## Fonctionnement technique

1. Le script vérifie si un fichier `schedule.json` existe:
   - Si non, il en crée un nouveau avec des entrées organisées aléatoirement
   - Si oui, il utilise la planification existante

2. Il calcule le jour actuel dans le cycle en fonction de la date de début et de la longueur du cycle

3. Si c'est le début d'un nouveau cycle, il:
   - Sauvegarde l'ancien cycle dans l'historique
   - Mélange à nouveau les entrées
   - Met à jour la date de début du cycle

4. Il génère le contenu du jour en utilisant l'entrée correspondante

5. Pour maintenir la planification entre les jours, les informations sont stockées dans `schedule.json`

## Prévention des doublons

Le script évite les doublons de texte dans un même cycle:

1. Chaque texte n'est utilisé qu'une seule fois si possible
2. Si moins de textes uniques sont disponibles que la longueur du cycle:
   - Le script affiche un avertissement
   - Il réutilise certains textes mais avec des combinaisons image/audio différentes
   - Il essaie de maximiser la diversité des combinaisons

Cette approche garantit une variété maximale tout en respectant la contrainte de la longueur du cycle configurée.
