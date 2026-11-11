# Lancer : python scripts/test_texts.py (depuis la racine du dépôt)
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from texts import extract_texts  # noqa: E402
from schedule import filter_texts  # noqa: E402


def doc(*paragraphs):
    """Simule le HTML d'un Google Doc publié : c1 est la classe italique."""
    body = "".join("<p>" + "".join(f'<span class="{c}">{t}</span>' for c, t in p) + "</p>"
                   for p in paragraphs)
    return ('<html><head><style>.c1{font-weight:400;font-style:italic}.c2{font-weight:400}</style></head>'
            f'<body><div id="contents">{body}</div></body></html>')


def p(text, cls="c2"):
    return [(cls, text)]


SEP = p("***")
LONG = "x" * 250


def test_entree_de_trois_paragraphes():
    html = doc(p("Intro hors entrée " + LONG), SEP, p("Un."), p("Deux."), p("Trois."), SEP, p("Suivante."), SEP)
    texts = filter_texts(extract_texts(html), 200, 400)
    assert "Un.<br><br>Deux.<br><br>Trois." in texts, texts
    assert "Suivante." in texts, texts


def test_bornes_hors_delimiteurs():
    html = doc(p("trop court"), p("assez long " + LONG), SEP, p("Entrée."), SEP)
    texts = filter_texts(extract_texts(html), 200, 400)
    assert "trop court" not in texts, texts
    assert "assez long " + LONG in texts, texts


def test_delimiteur_non_ferme():
    html = doc(SEP, p("Fermée."), SEP, p("Ouverte, jamais fermée " + LONG))
    texts = filter_texts(extract_texts(html), 200, 400)
    assert texts == ["Fermée."], texts


def test_delimiteur_colle_en_tete():
    html = doc(SEP, p("Première."), p("***Seconde."), SEP)
    texts = filter_texts(extract_texts(html))
    assert texts == ["Première.", "Seconde."], texts


def test_italiques_et_echappement():
    html = doc(SEP, [("c2", "Lire "), ("c1", "L’Évangile selon Luc"), ("c2", " &lt;script&gt;x&lt;/script&gt;")], SEP)
    texts = filter_texts(extract_texts(html))
    assert texts == ["Lire <em>L’Évangile selon Luc</em> &lt;script&gt;x&lt;/script&gt;"], texts


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
