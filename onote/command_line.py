"""Usage: onote search [-i <index>] QUERY
          onote index [-d <directory>]

-i <index>, --index <index>              Path to index directory
-d <directory>, --directory <directory>  Path to index directory
--version                                Show version
--help
"""

import concurrent.futures
import json
import logging
import os
import subprocess

from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
from docopt import docopt
from html.parser import HTMLParser
from pathlib import Path
from typing import Generator

from onote.auth import OneNoteAuthenticator, OneNoteSession

logger = logging.getLogger(__name__)

PAGES_URL = "https://graph.microsoft.com/v1.0/me/onenote/pages"

VERSION = 0.1
INDEX_DIR_PATH = Path(os.path.join(Path.home(), ".onote", "index"))


def create_index(path: Path):
    index_managed = path.joinpath(".managed.json")
    index_meta = path.joinpath("meta.json")
    if not path.exists():
        logger.info(f"Creating '{path}'")
        os.makedirs(path)
    if not index_managed.exists():
        logger.info(f"Creating '{index_managed}'")
        with open("index/.managed.json", "r") as r:
            with open(index_managed, "w") as w:
                w.write(r.read())
    if not index_meta.exists():
        logger.info(f"Creating '{index_meta}'")
        with open("index/meta.json", "r") as r:
            with open(index_meta, "w") as w:
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


class SearchError(Exception):
    pass


def index(index_path, downloader):
    """
    Onenote PAGES_URL returns paginated list pages.
    Idea is to concurrently download a list of page content urls and index in a single batch using tantivy
    """
    Page = namedtuple('Page', ['title', 'content_url', 'weblink'])

    def tantivy(pages):
        p = subprocess.run(["tantivy", "index", "--index", index_path],
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

                logger.info(f"Downloading content page '{page.title}' from '{page.content_url}'")

            pages_url = c.get("@odata.nextLink")

        # index pages
        logger.info("Indexing pages")
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


SearchResult = namedtuple('SearchResult', ['title', 'url'])


def search(query, index_path) -> Generator[SearchResult, None, None]:
    p = subprocess.run(["tantivy", "search", "--index", index_path, "-q", query],
                       encoding="utf8", capture_output=True)
    if p.returncode != 0:
        raise SearchError(p.stderr)
    for r in p.stdout.strip().split('\n'):
        c = json.loads(r)
        yield SearchResult(title=c["title"][0], url=c["url"][0])


def main():
    logging.basicConfig(level=logging.DEBUG)

    args = docopt(__doc__, version=VERSION)

    # index
    if args["index"]:
        path = Path(args["--directory"] if args["--directory"] else INDEX_DIR_PATH)
        logger.debug(f"Looking for index at path {path}")
        create_index(path)

        client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
        scopes = ["user.read", "notes.read"]
        user_name = "antonydeepak@gmail.com"
        authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
        downloader = OneNoteSession(authenticator).get
        try:
            index(path, downloader)
            exit(0)
        except IndexError as e:
            logger.error(f"Indexing failed with message '{e}'")
            exit(1)

    # search
    if args["search"]:
        q = args["QUERY"].strip()
        path = args["--index"] if args["--index"] else INDEX_DIR_PATH
        try:
            for r in search(q, path):
                print(f"title: {r.title}\nurl: {r.url}")
                print()
        except SearchError as e:
            logger.error(f"Search failed with message '{e}'")
            exit(1)
