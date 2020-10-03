import atexit
import msal
import os
import requests
import logging

from pathlib import Path
from typing import List

CACHE_PATH = Path(os.path.join(Path.home(), ".onote", "user_token.bin"))

logger = logging.getLogger(__name__)


class OneNoteAuthenticator():
    def __init__(self, user_name: str, client_id: str, scopes: List[str]):
        self.cache = msal.SerializableTokenCache()
        if CACHE_PATH.exists():
            self.cache.deserialize(open(CACHE_PATH, "r").read())
        atexit.register(self._serialize_cache)

        self.user_name = user_name
        self.app = msal.PublicClientApplication(
            client_id=client_id,
            token_cache=self.cache
        )
        self.scopes = scopes

    def __call__(self):
        """Uses device code flow
        Authorization code flow is annoying because it is meant to be used in servers which should be 
        time synced. Else, the token barfs because the time is slightly off when msal tries to decode """
        accounts = self.app.get_accounts(self.user_name)
        result = None
        if accounts:
            logger.info("account exists. User must have logged-in before. Taking the first account")
            result = self.app.acquire_token_silent(self.scopes, account=accounts[0])
        if not result:
            logger.info("Could not get the credentials. Using device flow")

            flow = self.app.initiate_device_flow(scopes=self.scopes)
            result = self.app.acquire_token_by_device_flow(flow)

        if "error" in result:
            raise Exception(result["error_description"])

        return result["access_token"]

    def _serialize_cache(self):
        if self.cache.has_state_changed:
            cache_dir = CACHE_PATH.parent
            if not cache_dir.exists():
                os.makedirs(cache_dir)
            open(CACHE_PATH, "w").write(self.cache.serialize())


class OneNoteSession(requests.Session):
    def __init__(self, token_fetcher: callable):
        super().__init__()

        self.token_fetcher = token_fetcher
        token = self.token_fetcher()
        self.headers.update(
            {"User-Agent": "onoteClient", "Authorization": f"Bearer {token}"}
        )

    def request(self, *args, **kwargs):
        resp = super().request(*args, **kwargs)
        if resp.status_code == 401:
            token = self.token_fetcher()
            self.headers["Authorization"] = f"Bearer {token}"
            resp = super().request(*args, **kwargs)
        return resp
