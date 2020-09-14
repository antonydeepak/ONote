from auth import OneNoteAuthenticator, OneNoteSession
from concurrent.futures import ThreadPoolExecutor
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


def download(session, url):
    logger.info(f"Downloading {url}")
    r = session.get(url)
    r.raise_for_status()
    return r.text


# create a threpool executor
# schedule the download in that exector
# gather all the promises
# get the result from the promises

async def main():
    client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    scopes = ["user.read", "notes.read"]
    # redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    user_name = "antonydeepak@gmail.com"

    authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
    s = OneNoteSession(authenticator)

    r = json.load(open("pages.json", "r"))
    loop = asyncio.get_running_loop()
    tasks = []
    with ThreadPoolExecutor() as pool:
        for p in r["value"]:
            url = p["contentUrl"]
            tasks.append(loop.run_in_executor(pool, download, s, url))
        content = await asyncio.gather(*tasks, return_exceptions=True)
        for c in content:
            print(c)

logging.basicConfig(level=logging.INFO)
asyncio.run(main())
