"""Configuration propre au backend API (privé).

Séparée de la config publique : ce fichier ne doit exister que dans le
sous-module privé.
"""

PROD = True

if PROD:
    URL_API = "https://www.ezfacture.fr"
    CLIENT_ID = "mxFaWuQIqXGclVldJB0WoCbmRirGJKNczmo5cuka"
else:
    URL_API = "http://127.0.0.1:8000"
    CLIENT_ID = "IuJifRCdZEg5TiGHvY2K9uU2MVXNFgTDtp5IJl3U"
