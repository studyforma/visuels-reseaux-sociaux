"""Rend un visuel HTML (ou un gabarit .dc.html du canvas) en PNG 1080 px de large.

Usage :
    python3 outils/rendu_png.py <fichier.html> <sortie.png> <largeur> <hauteur> [marque] [cle=valeur ...]

    marque : dossier de la marque dans ce dépôt (par défaut « studyforma »),
             dont le sous-dossier logos/ contient les logos nommés par leur identifiant de blob.
    cle=valeur : valeur des variables {{cle}} d'un gabarit (ex. fond=#52399A pour la couverture).
                 Le rendu s'arrête si une variable reste vide.

Le script :
  - retire le bloc <helmet> des gabarits du canvas ;
  - remplace les images « /_blob/<id> » par les logos du dossier <marque>/logos/ ;
  - répète le contenu des <sc-for> selon hint-placeholder-count ;
  - garde le premier <sc-if> d'une paire et supprime les suivants vides ;
  - charge la police Manrope depuis outils/polices/ ;
  - réduit la palette de couleurs (PNG plus léger, rendu identique à l'oeil).
"""
import re
import sys
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

DEPOT = Path(__file__).resolve().parent.parent
POLICES = DEPOT / "outils" / "polices"
GRAISSES = (400, 500, 600, 700)  # Regular, Medium, Semibold, Bold (charte Study Forma)


def preparer(html: str, logos: Path) -> str:
    corps = re.search(r"<x-dc>(.*)</x-dc>", html, re.S)
    corps = corps.group(1) if corps else html
    corps = re.sub(r"<helmet>.*?</helmet>", "", corps, flags=re.S)
    corps = re.sub(
        r'src="/_blob/([0-9a-f]{32})"',
        lambda m: f'src="file://{logos}/{m.group(1)}.svg"',
        corps,
    )

    def repeter(m):
        n = int(m.group(1))
        return m.group(2) * n

    corps = re.sub(
        r'<sc-for[^>]*hint-placeholder-count="(\d+)"[^>]*>(.*?)</sc-for>',
        repeter,
        corps,
        flags=re.S,
    )
    # sc-if : on garde le contenu du premier bloc d'une suite, on retire les suivants.
    blocs = list(re.finditer(r"<sc-if[^>]*>(.*?)</sc-if>", corps, flags=re.S))
    if blocs:
        sortie, pos, garde = [], 0, True
        for i, b in enumerate(blocs):
            sortie.append(corps[pos:b.start()])
            contigu = i > 0 and corps[blocs[i - 1].end():b.start()].strip() == ""
            garde = not contigu
            if garde:
                sortie.append(b.group(1))
            pos = b.end()
        sortie.append(corps[pos:])
        corps = "".join(sortie)
    faces = "\n".join(
        f"@font-face{{font-family:'Manrope';font-weight:{w};"
        f"src:url('file://{POLICES}/manrope-latin-{w}-normal.woff2') format('woff2')}}"
        for w in GRAISSES
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        f"<style>{faces}\nbody{{margin:0}}</style></head><body>{corps}</body></html>"
    )


def main():
    source, sortie, largeur, hauteur = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    extras = sys.argv[5:]
    variables = dict(a.split("=", 1) for a in extras if "=" in a)
    marques = [a for a in extras if "=" not in a]
    marque = marques[0] if marques else "studyforma"
    logos = DEPOT / marque / "logos"
    html = preparer(Path(source).read_text(encoding="utf-8"), logos)
    html = re.sub(
        r"\{\{\s*(\w+)\s*\}\}",
        lambda m: variables.get(m.group(1), m.group(0)),
        html,
    )
    restantes = sorted(set(re.findall(r"\{\{\s*(\w+)\s*\}\}", html)))
    if restantes:
        raise SystemExit(
            "Variables non renseignées : " + ", ".join(restantes)
            + " (ajouter par exemple fond=#52399A en argument)"
        )
    page = Path(sortie).resolve().with_suffix(".rendu.html")
    page.write_text(html, encoding="utf-8")
    with sync_playwright() as p:
        nav = p.chromium.launch()
        onglet = nav.new_page(viewport={"width": largeur, "height": hauteur})
        onglet.goto(f"file://{page}")
        onglet.evaluate("document.fonts.ready")
        onglet.wait_for_timeout(300)
        polices = onglet.evaluate("[...document.fonts].filter(f=>f.status==='loaded').length")
        onglet.locator("body > div").first.screenshot(path=sortie)
        nav.close()
    page.unlink()
    image = Image.open(sortie).convert("RGB")
    if image.size != (largeur, hauteur):
        raise SystemExit(f"Taille inattendue {image.size}, attendu {(largeur, hauteur)}")
    image.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
        sortie, optimize=True
    )
    if polices == 0:
        raise SystemExit("Police Manrope non chargée")
    print(f"OK {sortie} {image.size} polices chargées : {polices}")


if __name__ == "__main__":
    main()
