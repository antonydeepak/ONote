import msal
import requests
import webbrowser

client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
scopes = ["user.read", "notes.read"]
redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"

def get_authorization_code():
    # Uses authorization code flow of OAuth
    # Get the authorization code
    url = requests.Request(
        method='GET',
        url="https://login.microsoftonline.com/consumers/oauth2/v2.0/authorize",
        params={
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(scopes)
        }
    ).prepare().url
    webbrowser.open(url)

def get_access_token():
    # webbrowser opens and obtained code
    access_code = "M6eece65b-bd7d-2076-764b-677364f38c21"
    # Get the Access token
    app = msal.PublicClientApplication(
        client_id=client_id,
    )
    return app.acquire_token_by_authorization_code(
        code=access_code,
        scopes=scopes[:1],
        # redirect_uri=redirect_uri,
    )

def get_access_device_flow():
    app = msal.PublicClientApplication(
        client_id=client_id,
    )
    flow = app.initiate_device_flow(scopes=scopes)
    print(flow)
    return app.acquire_token_by_device_flow(flow)

def get_token_again():
    user_name = "antonydeepak@gmail.com"
    app = msal.PublicClientApplication(
        client_id=client_id,
    )
    accounts = app.get_accounts(user_name)
    result = None
    if accounts:
        print("no account")
        result = app.acquire_token_silent(scopes, account=accounts[0])
    if not result:
        print("no result")
    return result

if __name__ == '__main__':
    # get_authorization_code()
    # print(get_access_token())
    # print(get_access_device_flow())
    print(get_token_again())
