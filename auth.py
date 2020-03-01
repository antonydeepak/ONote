import msal
import requests
import webbrowser
import os, atexit

client_id = "543ead0b-cc06-487c-9b75-67213f2d5fff"
scopes = ["user.read", "notes.read"]
redirect_uri = "https://login.microsoftonline.com/common/oauth2/nativeclient"
user_name = "antonydeepak@gmail.com"

home = '/home/antonydeepak'
cache = ".cache"
onenotelinux = "onenotelinux"
cache_name = "user_token.bin"
cache_location = os.path.join(home, cache, onenotelinux, cache_name)
cache = msal.SerializableTokenCache()
if os.path.exists(cache_location):
    cache.deserialize(open(cache_location, "r").read())
# optionally try `if cache.has_state_changed`
atexit.register(lambda: open(cache_location, "w").write(cache.serialize()))


def get_access_token():
    app = msal.PublicClientApplication(
        client_id=client_id,
        token_cache=cache
    )

    accounts = app.get_accounts(user_name)
    result = None
    if accounts:
        print("account exists. User must have logged-in before. Taking the first account")
        result = app.acquire_token_silent(scopes, account=accounts[0])
    if not result:
        print("Could not get the credentials. Using interactive flow")

        # webbrowser opens and obtained code
        get_authorization_code()
        access_code = input("Paste access code and hit enter once you have the token: ")
        result = app.acquire_token_by_authorization_code(
            code=access_code,
            scopes=scopes[:1])

    return result


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


def get_access_device_flow():
    app = msal.PublicClientApplication(
        client_id=client_id,
        token_cache=cache
    )
    flow = app.initiate_device_flow(scopes=scopes)
    print(flow)
    return app.acquire_token_by_device_flow(flow)

if __name__ == '__main__':
    # print(get_access_device_flow())
    print(get_access_token())
