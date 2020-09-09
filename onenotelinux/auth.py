import atexit
import msal
import os
import requests
import logging

from pathlib import Path
from typing import List

CACHE_PATH = Path(os.path.join(Path.home(), ".cache", "onenotelinux", "user_token.bin"))

logger = logging.getLogger(__name__)


def _serialize_cache(cache: msal.TokenCache):
    if cache.has_state_changed:
        cache_dir = CACHE_PATH.parent
        if not cache_dir.exists():
            os.makedirs(cache_dir)
        open(CACHE_PATH, "w").write(cache.serialize())


class OneNoteAuthenticator():
    def __init__(self, user_name: str, client_id: str, scopes: List[str], token_cache: msal.TokenCache):
        self.scopes = scopes
        self.app = msal.PublicClientApplication(
            client_id=client_id,
            token_cache=cache
        )

    def __call__(self):
        """Uses device code flow
        Authorization code flow is annoying because it is meant to be used in servers which should be 
        time synced. Else, the token barfs because the time is slightly off when msal tries to decode """
        accounts = self.app.get_accounts(user_name)
        result = None
        if accounts:
            logger.debug("account exists. User must have logged-in before. Taking the first account")
            result = self.app.acquire_token_silent(scopes, account=accounts[0])
        if not result:
            logger.debug("Could not get the credentials. Using device flow")

            flow = self.app.initiate_device_flow(scopes=scopes)
            print(flow["message"])
            result = self.app.acquire_token_by_device_flow(flow)

        if "error" in result:
            raise Exception(result["error_description"])

        return result["access_token"]


class OneNoteSession(requests.Session):
    def __init__(self, token_fetcher: callable):
        super().__init__()

        self.token_fetcher = token_fetcher
        token = self.token_fetcher()
        self.headers.update(
            {"User-Agent": "OnenoteLinuxClient", "Authorization": f"Bearer {token}"}
        )

    def request(self, *args, **kwargs):
        resp = super().request(*args, **kwargs)
        if resp.status_code == 401:
            token = self.token_fetcher()
            self.headers["Authorization"] = f"Bearer {token}"
            resp = super().request(*args, **kwargs)
        return resp


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # print(get_access_device_flow())
    client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    scopes = ["user.read", "notes.read"]
    redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    user_name = "antonydeepak@gmail.com"

    cache = msal.SerializableTokenCache()
    if CACHE_PATH.exists():
        cache.deserialize(open(CACHE_PATH, "r").read())
    atexit.register(_serialize_cache, cache)

    authenticator = OneNoteAuthenticator(user_name, client_id, scopes, cache)
    s = OneNoteSession(authenticator)
