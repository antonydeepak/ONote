from auth import OneNoteAuthenticator, OneNoteSession
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import logging
import asyncio

logger = logging.getLogger(__name__)


def download(session, url):
    logger.info(f"Downloading {url}")
    if "0-b1d74c2970a3463f9344bdf6fee47eb8!50-F33E492FF42DEBDD" in url:
        raise ValueError("Download Failed")
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
    with ProcessPoolExecutor() as pool:
        for p in r["value"]:
            url = p["contentUrl"]
            tasks.append(loop.run_in_executor(pool, download, s, url))
        content = await asyncio.gather(*tasks, return_exceptions=False)
        print(type(content[0]))
        print(content[1])

logging.basicConfig(level=logging.INFO)
asyncio.run(main())
