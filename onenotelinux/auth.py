import atexit
import msal
import os

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
    account = accounts[0]
    result = None
    if accounts:
        print("account exists. User must have logged-in before. Taking the first account")
        result = app.acquire_token_silent(scopes, account=accounts[0])
    if not result:
        print("Could not get the credentials. Using device flow")

        # Authorization code flow is annoying because it is meant to be used in servers which should be 
        # time synced. Else, the token barfs because the time is slightly off when msal tries to decode
        flow = app.initiate_device_flow(scopes=scopes)
        result = app.acquire_token_by_device_flow(flow)

    return (account, result['access_token'])


if __name__ == '__main__':
    # print(get_access_device_flow())
    print(get_access_token())
