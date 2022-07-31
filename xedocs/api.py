import os
from warnings import warn

import rframe


def api_client(url, token=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    client = rframe.RestClient(
        url,
        headers=headers,
    )
    return client


def api_token(
    username=None, password=None, readonly=True, audience="https://api.cmt.xenonnt.org"
):
    import xeauth

    if readonly:
        scopes = ["read:all", "write:all"]
    else:
        scopes = ["read:all"]

    xetoken = xeauth.login(
        username=username, password=password, scopes=scopes, audience=audience
    )

    return xetoken.access_token
