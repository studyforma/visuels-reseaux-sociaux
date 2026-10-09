"""Rend un reel animé (HTML) en vidéo MP4 1080 x 1920, image par image.

Usage :
    python3 outils/rendu_reel.py <reel.html> <sortie.mp4> [marque] [ips]

Le fichier HTML doit définir :
  - window.DUREE : durée totale en secondes ;
  - window.rendre(t) : met la page dans l'état de l'instant t (en secondes).
Le rendu est déterministe : chaque image est calculée, puis capturée.
Les logos « /_blob/<id> » et la police Manrope sont gérés comme dans rendu_png.py.
Une piste audio silencieuse est ajoutée (le son tendance est posé ensuite dans Metricool ou Instagram).
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rendu_png import DEPOT, preparer  # noqa: E402

LARGEUR, HAUTEUR = 1080, 1920


def main():
    source, sortie = sys.argv[1], sys.argv[2]
    marque = sys.argv[3] if len(sys.argv) > 3 else "studyforma"
    ips = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    logos = DEPOT / marque / "logos"
    dossier = Path(tempfile.mkdtemp(prefix="reel_"))
    page_html = dossier / "reel.html"
    page_html.write_text(preparer(Path(source).read_text(encoding="utf-8"), logos), encoding="utf-8")
    with sync_playwright() as p:
        nav = p.chromium.launch()
        onglet = nav.new_page(viewport={"width": LARGEUR, "height": HAUTEUR})
        onglet.goto(f"file://{page_html}")
        onglet.evaluate("document.fonts.ready")
        onglet.wait_for_timeout(300)
        duree = float(onglet.evaluate("window.DUREE"))
        total = int(round(duree * ips))
        for i in range(total):
            onglet.evaluate(f"window.rendre({i / ips})")
            onglet.screenshot(path=str(dossier / f"img_{i:05d}.png"), clip={"x": 0, "y": 0, "width": LARGEUR, "height": HAUTEUR})
        nav.close()
    commande = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(ips), "-i", str(dossier / "img_%05d.png"),
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-shortest", "-c:v", "libx264", "-preset", "slow", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        sortie,
    ]
    subprocess.run(commande, check=True)
    shutil.rmtree(dossier)
    print(f"OK {sortie} : {total} images, {duree:.1f} s, {ips} images/s")


if __name__ == "__main__":
    main()
