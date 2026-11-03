import logging
from datetime import datetime

import requests

from controller.backends.base import NumberingBackend
from controller.backends.api.ezauth import EzOauth2
from controller.backends.api.config import URL_API

logger = logging.getLogger(__name__)


class ApiBackend(NumberingBackend):
    """Numérotation via l'API ezfacture (OAuth2 PKCE).

    Les numéros de factures sont réservés et validés côté serveur. La réservation
    est immédiate (POST /create) ; le rollback appelle DELETE /cancel avec le
    ``cancel_token`` renvoyé par le serveur.
    """

    requires_auth = True

    def __init__(self, controller):
        super().__init__(controller)
        self.access_token = None
        self.cancel_token = None

    # ------------------------------------------------------------------ #
    # Authentification
    # ------------------------------------------------------------------ #

    def login(self):
        auth = EzOauth2()
        self.access_token = auth.get_access_token()
        return self.access_token

    def _authenticated_request(self, method, url, **kwargs):
        """Exécute une requête HTTP avec le token Bearer courant.

        Sur 401 : tente un refresh silencieux (sans ouvrir de navigateur).
        Si le refresh échoue, bloque l'UI et demande à l'utilisateur de se reconnecter.
        """
        view = self.controller.view
        extra_headers = kwargs.pop("headers", {})

        def _do(token):
            headers = {**extra_headers, "Authorization": f"Bearer {token}"}
            return requests.request(method, url, headers=headers, **kwargs)

        response = _do(self.access_token)

        if response.status_code == 401:
            logger.warning("Requête rejetée (401), tentative de refresh silencieux...")
            new_token = EzOauth2().try_silent_refresh()
            if new_token:
                self.access_token = new_token
                response = _do(new_token)
            else:
                self.access_token = None
                view.block_ui()
                view.buttons["connexion"].configure(state="normal")
                view.show_feedback(
                    txt="Session expirée. Merci de vous reconnecter.",
                    message_type="error"
                )

        return response

    # ------------------------------------------------------------------ #
    # Interface NumberingBackend
    # ------------------------------------------------------------------ #

    def get_number(self, type_doc="facture"):
        """:return: nouveau numéro de facture, ou lève une ValueError si erreur."""
        url = f"{URL_API}/ezexcel/factures/last/?type={type_doc}"
        response = self._authenticated_request("GET", url)
        if response.status_code == 200:
            resp = response.json()
            last_num_fact = resp["numeroFacture"]

            today = datetime.now()
            prefix = "AV" if type_doc == "avoir" else "FAC"
            year_month_prefix = f"{prefix}-{today.year}-{today.month:02d}"

            if last_num_fact == 0 or last_num_fact == "0":
                new_num_fact = f"{year_month_prefix}-00001"
            else:
                last_seq = int(last_num_fact.split('-')[-1])
                new_num_fact = f"{year_month_prefix}-{last_seq + 1:05d}"

            return new_num_fact
        else:
            raise ValueError(
                f"Impossible de récupérer le dernier numéro de facture : "
                f"statut code {response.status_code}"
            )

    def reserve(self, number, type_doc="facture"):
        """Crée le numéro côté serveur et mémorise le cancel_token.

        Le paramètre ``number`` n'est pas utilisé : c'est le serveur qui fait foi.
        Aucune ``entry`` à committer côté client (retourne None).
        """
        url = f"{URL_API}/ezexcel/factures/create/"
        response = self._authenticated_request("POST", url, json={"type": type_doc})

        if response.status_code == 201:
            resp = response.json()
            self.cancel_token = resp["cancel_token"]
            return None
        else:
            raise ValueError("Impossible de créer le numéro de facture.")

    def commit(self, entry):
        # L'API a déjà écrit lors de la réservation → rien à faire.
        return True

    def cancel(self, number):
        url = f"{URL_API}/ezexcel/factures/cancel/{number}/"
        response = self._authenticated_request(
            "DELETE", url,
            headers={"X-Cancel-Token": self.cancel_token}
        )

        if response.status_code in [200, 404]:
            # 200 -> supprimé ; 404 -> déjà supprimé/inexistant -> ok pour un rollback
            return True
        else:
            raise ValueError(f"Impossible d'annuler la facture {number}.")
