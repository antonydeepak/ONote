import requests
import json
from onenotelinux.auth import get_access_token
from onenotelinux.model import Notebook

BASE_URL_TEMPLATE = "https://graph.microsoft.com/v1.0/me/onenote/"
NOTEBOOKS_URL = requests.compat.urljoin(BASE_URL_TEMPLATE, "notebooks")


def get_onenote_base_url(account_name):
    return BASE_URL_TEMPLATE.format(account_name)


# get notebooks
def get_notebooks():
    account_name, access_token = get_access_token()
    auth_headers = {
        'Authorization': f'Bearer {access_token}'
    }
    response = requests.get(NOTEBOOKS_URL, headers=auth_headers)
    notebooks_response = json.loads(response.text)['value']
    return (
        Notebook(notebook['id'], notebook['displayName'])
        for notebook in notebooks_response
    )
