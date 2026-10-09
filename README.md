# visuels-reseaux-sociaux

Visuels des publications Instagram, Facebook et LinkedIn de Study Forma, programmées ensuite dans Metricool.

Ce dépôt est **public** : n'y déposer que des visuels validés, juste avant leur programmation.

## Organisation

| Dossier | Contenu |
|---|---|
| `outils/rendu_png.py` | Transforme un visuel HTML (ou un gabarit du canvas) en PNG |
| `outils/rendu_reel.py` | Transforme un reel animé (HTML) en vidéo MP4 1080 x 1920 |
| `outils/polices/` | Police Manrope, graisses Regular, Medium, Semibold et Bold (licence OFL, voir `OFL.txt`) |
| `photos/` | Photos libres de droits téléchargées par le robot (voir plus bas) |
| `studyforma/logos/` | Logos Study Forma, nommés par leur identifiant dans le canvas des gabarits |
| `studyforma/AAAA-MM/` | Visuels validés du mois (ex. `studyforma/2026-11/`) |

## Rendu d'un visuel

```
python3 outils/rendu_png.py visuel.html visuel.png 1080 1350
python3 outils/rendu_png.py story.html story.png 1080 1920
python3 outils/rendu_png.py couverture.dc.html couverture.png 1080 1350 fond=#52399A
python3 outils/rendu_reel.py reel.html reel.mp4
```

## Photos libres de droits

Ajouter une ligne par photo dans `photos/a-telecharger.txt` (`nom-du-fichier.jpg URL`), puis pousser : le robot `.github/workflows/photos.yml` télécharge les images dans `photos/` et vide la liste.

## Lien public d'un visuel

`https://raw.githubusercontent.com/studyforma/visuels-reseaux-sociaux/main/<chemin du fichier>`

Metricool récupère l'image ou la vidéo à partir de ce lien au moment de la programmation et en garde sa propre copie.
