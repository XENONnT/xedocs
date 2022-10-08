import os
import rframe
import requests

from ._settings import settings


class RestClient(rframe.RestClient):
    _token = None
    
    @property
    def token(self):
        if self._token is None:
            settings.get_api_token()
        return self._token

    @property
    def headers(self):
        if "Authorization" not in self._headers and self.token:
            self._headers["Authorization"] = f"Bearer {self.token}"
        return self._headers

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

    client = RestClient(
        url,
        headers=headers,
    )
    return client

