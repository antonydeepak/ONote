# sets up the fundamentals from py
# It enumerates thru pages in /page
# for every page it give it to a process pool executor (failures during indexing)
import asyncio
import json
import logging
import os
import atexit
import subprocess

from auth import OneNoteAuthenticator, OneNoteSession
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
from collections import namedtuple

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PAGES_URL = "https://graph.microsoft.com/v1.0/me/onenote/pages"

Page = namedtuple('Page', ['title', 'content_url', 'weblink'])

INDEX_DIR_PATH = Path(os.path.join(Path.home(), ".onenotelinux", "index"))
INDEX_MANAGED = INDEX_DIR_PATH.joinpath(".managed.json")
INDEX_META = INDEX_DIR_PATH.joinpath("meta.json")
if not INDEX_DIR_PATH.exists():
    logger.debug(f"Creating '{INDEX_DIR_PATH}'")
    os.makedirs(INDEX_DIR_PATH)
if not INDEX_MANAGED.exists():
    logger.debug(f"Creating '{INDEX_MANAGED}'")
    with open("index/.managed.json", "r") as r:
        with open(INDEX_MANAGED, "w") as w:
            w.write(r.read())
if not INDEX_META.exists():
    logger.debug(f"Creating '{INDEX_META}'")
    with open("index/meta.json", "r") as r:
        with open(INDEX_META, "w") as w:
            w.write(r.read())


class HtmlOnenoteContentParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.is_ptag = False
        self._content = []

    def handle_starttag(self, tag, attrs):
        self.is_ptag = (tag == "p")

    def handle_data(self, data):
        if self.is_ptag:
            self._content.append(data)

    @property
    def content(self):
        return " ".join(self._content)


class IndexError(Exception):
    pass


def index_pages(pages, downloader):
    def tantivy(pages):
        p = subprocess.run(["tantivy", "index", "--index", INDEX_DIR_PATH],
                           input=pages, encoding="utf8", stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise IndexError(p.stderr)

    async def main(pages):
        loop = asyncio.get_running_loop()

        # download the OneNote page content
        tasks = []
        with ThreadPoolExecutor() as pool:
            for page in pages:
                logger.debug(f"Download content page '{page.title}' from '{page.content_url}'")
                tasks.append(loop.run_in_executor(pool, downloader, page.content_url))
        contents = await asyncio.gather(*tasks, return_exceptions=False)

        # index the page content
        indexable_pages = []
        for i, page in enumerate(pages):
            content_parser = HtmlOnenoteContentParser()
            content = contents[i].text
            content_parser.feed(content)
            content = content_parser.content

            indexable_pages.append(json.dumps({
                "title": page.title,
                "content": content,
                "url": page.weblink
            }))
        tantivy("\n".join(indexable_pages))

    asyncio.run(main(pages))


async def index(downloader):
    """
    Onenote PAGES_URL returns paginated list pages.
    Idea is to download a list of page content urls and concurrently schedule it for indexing in a separate process
        - Inside that process, we concurrently download the content for all the pages
        - We then batch that up and sent it to tantivy for indexing
    """

    index_tasks = []
    loop = asyncio.get_running_loop()
    with ProcessPoolExecutor() as pool:
        pages_url = PAGES_URL
        while pages_url is not None:
            logger.debug(f"Downloading {pages_url}")
            r = downloader(pages_url)
            r.raise_for_status()

            c = json.loads(r.text)
            pages = c["value"]
            indexable_pages = [
                Page(title=page["title"], content_url=page["contentUrl"],
                     weblink=page["links"]["oneNoteWebUrl"]["href"])
                for page in pages
            ]
            if indexable_pages:
                index_tasks.append(loop.run_in_executor(pool, index_pages, indexable_pages, downloader))

            pages_url = c.get("@odata.nextLink")
        index_results = await asyncio.gather(*index_tasks, return_exceptions=True)
        failed_tasks = ((index_tasks[i], r) for i, r in enumerate(index_results) if isinstance(r, Exception))
        for t, r in failed_tasks:
            logger.warning(f"Failed to index {t} because {r}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    scopes = ["user.read", "notes.read"]
    redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    user_name = "antonydeepak@gmail.com"

    authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
    s = OneNoteSession(authenticator)
    asyncio.run(index(downloader=s.get))
