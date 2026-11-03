import webbrowser
import requests
from urllib.parse import urlencode
from threading import Thread, Event
import random
import string
import base64
import hashlib
from werkzeug.serving import make_server
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
import json
import os
import time
import logging
from controller.backends.api.config import URL_API, CLIENT_ID

logger = logging.getLogger(__name__)


class CacheFileHandler:
    def __init__(self, cache_path=None):
        self.cache_path = cache_path or ".token_cache"

    def save_token_to_cache(self, token_info):
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(token_info, f)
        except IOError as e:
            logger.info(f"Erreur lors de la sauvegarde du token dans le fichier cache: {e}")

    def get_cached_token(self):
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
            except (IOError, json.JSONDecodeError) as e:
                logger.info(f"Erreur lors de la lecture du fichier cache: {e}")
        logger.debug(f"Pas de fichier de cache token.")
        return None

    def delete_cached_token(self):
        if os.path.exists(self.cache_path):
            try:
                os.remove(self.cache_path)
            except IOError as e:
                logger.info(f"Erreur lors de la suppression du fichier cache: {e}")


class EzOauth2:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.redirect_uri = "http://127.0.0.1:8080/callback"
        self.authorization_url = f"{URL_API}/o/authorize/"
        self.token_url = f"{URL_API}/o/token/"
        self.cacheFileHandler = CacheFileHandler()

        self.access_token = None
        self.refresh_token = None
        self.auth_complete_event = Event()

        # Mapping des routes avec Werkzeug
        self.url_map = Map([Rule("/callback", endpoint="callback")])
        self.server = None
        self.server_thread = None

        # PKCE
        self.code_verifier = self._generate_code_verifier()
        self.code_challenge = self._generate_code_challenge(self.code_verifier)

    @staticmethod
    def _generate_code_verifier(length=128):
        """Génère un code verifier aléatoire pour PKCE."""
        verifier = "".join(random.choices(string.ascii_letters + string.digits, k=length))
        return verifier

    @staticmethod
    def _generate_code_challenge(verifier):
        """Génère le code challenge correspondant au code verifier."""
        digest = hashlib.sha256(verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")

    def generate_auth_url(self):
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "read write",
            "code_challenge": self.code_challenge,
            "code_challenge_method": "S256",
        }
        return f"{self.authorization_url}?{urlencode(params)}"

    def authenticate_user(self):
        auth_url = self.generate_auth_url()
        webbrowser.open(auth_url)

    def callback(self, request):
        auth_code = request.args.get("code")
        if not auth_code:
            self.auth_complete_event.set()
            return Response("Erreur: aucun code d'autorisation reçu.", status=400)

        # PKCE : on n'envoie pas le client_secret
        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code_verifier": self.code_verifier,
        }

        token_response = requests.post(self.token_url, data=data)
        token_data = token_response.json()

        if "access_token" in token_data:
            self.access_token = token_data["access_token"]
            self.refresh_token = token_data.get("refresh_token")
            token_data["expires_at"] = int(time.time()) + token_data.get("expires_in", 0)
            self.cacheFileHandler.save_token_to_cache(token_data)
            self.auth_complete_event.set()
            return Response("Connexion réussie ! Vous pouvez fermer cette fenêtre.")
        else:
            self.auth_complete_event.set()
            return Response(f"Erreur lors de l'obtention du token : {token_data}", status=400)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        urls = self.url_map.bind_to_environ(environ)
        try:
            endpoint, args = urls.match()
            if endpoint == "callback":
                response = self.callback(request)
        except Exception as e:
            response = Response(f"Erreur: {e}", status=500)
        return response(environ, start_response)

    def start_werkzeug_server(self):
        self.server = make_server("localhost", 8080, self.wsgi_app)
        self.server.serve_forever()

    def stop_server(self):
        if self.server:
            self.server.shutdown()

    @staticmethod
    def _cache_structure_valid(token_info):
        """Vérifie que le cache contient les champs requis."""
        return isinstance(token_info, dict) and {
            "access_token", "refresh_token", "expires_at"
        }.issubset(token_info.keys())

    def refresh_access_token(self, refresh_token):
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code == 200:
            token_info = response.json()
            token_info["expires_at"] = int(time.time()) + token_info.get("expires_in", 0)
            self.cacheFileHandler.save_token_to_cache(token_info)
            self.access_token = token_info["access_token"]
            logger.info("Rafraîchissement du token OK.")
            return self.access_token
        else:
            logger.error("Erreur lors du rafraîchissement du token.")
            return None

    def try_silent_refresh(self):
        """Tente un refresh sans interaction utilisateur. Retourne le nouveau token ou None.

        Utilisé par le controller pour gérer les réponses 401 en cours d'opération,
        sans ouvrir de navigateur.
        """
        token_info = self.cacheFileHandler.get_cached_token()
        if token_info and "refresh_token" in token_info:
            return self.refresh_access_token(token_info["refresh_token"])
        return None

    def get_access_token(self):
        """Retourne un access token validé côté serveur.

        Valide toujours via le refresh token (appel réseau) pour résister à la falsification
        du fichier cache (modifier expires_at ne suffit pas à contourner l'authentification).
        Si le refresh échoue, supprime le cache corrompu/révoqué et lance une auth complète.
        """
        token_info = self.cacheFileHandler.get_cached_token()

        if token_info:
            if not self._cache_structure_valid(token_info):
                logger.warning("Cache token invalide ou altéré, suppression.")
                self.cacheFileHandler.delete_cached_token()
            else:
                # Validation côté serveur via le refresh token
                new_token = self.refresh_access_token(token_info["refresh_token"])
                if new_token:
                    return new_token
                # Refresh refusé = session révoquée ou expirée côté serveur
                logger.warning("Refresh token refusé par le serveur.")
                self.cacheFileHandler.delete_cached_token()

        # Authentification complète requise
        self.server_thread = Thread(target=self.start_werkzeug_server)
        self.server_thread.daemon = True
        self.server_thread.start()

        self.authenticate_user()
        received = self.auth_complete_event.wait(timeout=120)
        self.stop_server()
        if not received:
            logger.warning("Timeout authentification (120s) : aucune réponse du navigateur.")

        return self.access_token
