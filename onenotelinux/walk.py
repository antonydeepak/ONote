import json
import logging
import os
import subprocess

from auth import OneNoteAuthenticator, OneNoteSession
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
# check if session works
# get all the notebooks pages locally

# parse the response into title, content, url. Dont' store content, but store title and url. index content and title
# use the schema to call tantivy for indexing

# Get all pages with https://graph.microsoft.com/v1.0/me/onenote/pages
# Keep using the nextLink to navigate to next pages. This will stop appearing in the last page.
# from the /pages extract the content url & title

client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
scopes = ["user.read", "notes.read"]
redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
user_name = "antonydeepak@gmail.com"


class HtmlOnenoteContentParse(HTMLParser):
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


authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
s = OneNoteSession(authenticator)
INDEX_DIR_PATH = Path(os.path.join(Path.home(), ".onenotelinux", "index"))
if not INDEX_DIR_PATH.exists():
    os.makedirs(INDEX_DIR_PATH)
PAGES_URL = "https://graph.microsoft.com/v1.0/me/onenote/pages"

# Download a page and send it for indexing. (indexing for a batch of pages would be a single unit for concurrency)
# Continue to download
# Wrap all this in a nice tui similar to fzf?
# Give a command line interface that can refresh
# Give a command line interface that can search

# Progress
    # parallel indexing in different processes
# will 
def index_pages():
    logging.debug("Fetching pages")
    r = s.get(PAGES_URL)
    r.raise_for_status()

    c = json.loads(r.text)
    pages = c["value"]
    indexable_pages = []
    for page in pages:
        title = page["title"]

        content_url = page["contentUrl"]
        r = s.get(content_url)
        content_parser = HtmlOnenoteContentParse()
        content_parser.feed(r.text)
        content = content_parser.content

        url = page["links"]["oneNoteWebUrl"]["href"]

        indexable_pages.append(json.dumps({
            "title": title,
            "content": content,
            "url": url
        }))
    logging.debug(f"first page {indexable_pages[0]}")
    pages = "\n".join(indexable_pages)
    p = subprocess.run(["tantivy", "index", "--index", INDEX_DIR_PATH], input=pages, encoding="utf8")
    return p.returncode


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    scopes = ["user.read", "notes.read"]
    redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    user_name = "antonydeepak@gmail.com"

    authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
    s = OneNoteSession(authenticator)
    r = s.get("https://graph.microsoft.com/v1.0/me/onenote/pages")
    r.raise_for_status()
    p = open("pages.json", "w")
    p.write(r.text)
    p.flush()

    # p = HtmlOnenoteContentParse()
    # p.feed(open("page.html", "r").read())
    # print(p.content)
    # index("https://graph.microsoft.com/v1.0/users/me/onenote/pages/0-a03623f19fed436ebc0657fddc45a2fd!19-F33E492FF42DEBDD!324082/content")
    # print(index_pages())