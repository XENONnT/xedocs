import os
import rframe
import requests

from ._settings import settings


class RestClient(rframe.RestClient):
    _token = None
    
    @property
    def token(self):
        if self._token is None:
            self._token = api_token()
        return self._token

    @property
    def headers(self):

        if "Authorization" not in self._headers and self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"

    def __init__(self, url, token=None, headers=None, client=None) -> None:
        self.base_url = url
        self._headers = headers if headers is not None else {}
        self._token = token

        if client is None:
            client = requests
        self.client = client


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
