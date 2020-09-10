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
# Keep using the nextLink to navigate to next pages

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
content_parser = HtmlOnenoteContentParse()
INDEX_DIR_PATH = Path(os.path.join(Path.home(), ".onenotelinux", "index"))
if not INDEX_DIR_PATH.exists():
    os.makedirs(INDEX_DIR_PATH)


def index(page_url):
    c = s.get(page_url)
    content_parser.feed(c.text)
    c = content_parser.content
    p = subprocess.run(["tantivy", "index", "--index", INDEX_DIR_PATH], input=c, encoding="utf8")
    print(p.returncode)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # print(get_access_device_flow())
    # client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
    # scopes = ["user.read", "notes.read"]
    # redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
    # user_name = "antonydeepak@gmail.com"

    # authenticator = OneNoteAuthenticator(user_name, client_id, scopes)
    # s = OneNoteSession(authenticator)
    # r = s.get("https://graph.microsoft.com/v1.0/users/me/onenote/pages/0-a03623f19fed436ebc0657fddc45a2fd!19-F33E492FF42DEBDD!324082/content")
    # r.raise_for_status()
    # p = open("page.html", "w")
    # p.write(r.text)
    # p.flush()

    # p = HtmlOnenoteContentParse()
    # p.feed(open("page.html", "r").read())
    # print(p.content)
    index("https://graph.microsoft.com/v1.0/users/me/onenote/pages/0-a03623f19fed436ebc0657fddc45a2fd!19-F33E492FF42DEBDD!324082/content")
