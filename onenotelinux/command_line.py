import concurrent.futures
import json
import logging
import os
import subprocess

from auth import OneNoteAuthenticator, OneNoteSession
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

PAGES_URL = "https://graph.microsoft.com/v1.0/me/onenote/pages"


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


def index(downloader):
    """
    Onenote PAGES_URL returns paginated list pages.
    Idea is to concurrently download a list of page content urls and index in a single batch using tantivy
    """
    Page = namedtuple('Page', ['title', 'content_url', 'weblink'])

    def tantivy(pages):
        p = subprocess.run(["tantivy", "index", "--index", INDEX_DIR_PATH],
                           input=pages, encoding="utf8", stderr=subprocess.PIPE)
        if p.returncode != 0:
            raise IndexError(p.stderr)

    future_to_page = {}
    with ThreadPoolExecutor() as executor:
        # download page content
        pages_url = PAGES_URL
        while pages_url is not None:
            logger.debug(f"Downloading {pages_url}")
            r = downloader(pages_url)
            r.raise_for_status()

            c = json.loads(r.text)
            pages = c["value"]
            for p in pages:
                page = Page(title=p["title"], content_url=p["contentUrl"], weblink=p["links"]["oneNoteWebUrl"]["href"])
                future = executor.submit(downloader, page.content_url)
                future_to_page[future] = page

                logger.debug(f"Downloading content page '{page.title}' from '{page.content_url}'")

            pages_url = c.get("@odata.nextLink")

        # index pages
        logger.debug("Indexing pages")
        indexable_pages = []
        for future in concurrent.futures.as_completed(future_to_page):
            page = future_to_page[future]
            if future.exception():
                logger.warning(f"Failed to index {page.title} because {future.exception()}")
                continue

            r = future.result()
            content_parser = HtmlOnenoteContentParser()
            content_parser.feed(r.text)
            content = content_parser.content

            indexable_pages.append(json.dumps({
                "title": page.title,
                "content": content,
                "url": page.weblink
            }))
        d = "\n".join(indexable_pages)
        tantivy(d)

        logger.info(f"Total {len(indexable_pages)} pages have been indexed")


if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    scopes = ["user.read", "notes.read"]
    redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    user_name = "antonydeepak@gmail.com"

    authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
    downloader = OneNoteSession(authenticator).get
    index(downloader)
