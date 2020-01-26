## Plan:
Authentication
	Client need to authenticate once
	Client after auth. Should be able to seamlessly access the application
	Revoking access should trigger a flow again.
	Auth should be intuitive to the clients.
	
Get
Update
Distribution


## Status:
Try out https://github.com/AzureAD/microsoft-authentication-library-for-python
When user opens the application prompt get the token and be able to make graph calls




## Random
```
    Authorization flow pattern
    # Use cases:
    #   when the user logs in for the first time
    #   when the user logs in again
    #   when the user logs out
    # Algorithm:
    #   idea is to use a file system based cache
    #   create a seriazable token cache from file system
    #   check if the token cache path exists 
    #       if yes, then restore the cache from that location
    #       if no, then do nothing; cache will be serialized on application exit
    #   create an app from that token cache
    #       try to use get_accounts (guess this retrieves from cache)
    #       if there is an account
    #           try to acquire token using the silent method; this should use both the cache and the refresh token from the cache
    #       if all fails then initiate a device flow
    # Api:
    #   get_access_token()
    # To ChecK
    #   what gets serialized and deserialized during the cache serialization; Looks like both refresh token, real token & user name should get serialized
    #   Maybe this won't be readable
    #   Just implement the method and see what happens 
```

## Notes Page
(Notes)[https://onedrive.live.com/view.aspx?resid=F33E492FF42DEBDD%2114266&id=documents&wd=target%28Projects.one%7C718D3450-986C-4BDB-839E-BF7256D2E2DA%2FProject%20Plan%7C005E97A0-2FBC-4E98-9E3E-95A5C75404D6%2F%29
onenote:https://d.docs.live.net/f33e492ff42debdd/Documents/Personal/Projects.one#Project%20Plan&section-id={718D3450-986C-4BDB-839E-BF7256D2E2DA}&page-id={005E97A0-2FBC-4E98-9E3E-95A5C75404D6}&end]
