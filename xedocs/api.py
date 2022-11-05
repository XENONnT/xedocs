import os
from typing import Mapping
import rframe
import requests
from requests import PreparedRequest
from requests.auth import AuthBase

from ._settings import settings


class ApiAuth(AuthBase):
    authenticator = None

    @property
    def token(self):
        if isinstance(self.authenticator, str):
            return self.authenticator
        if hasattr(self.authenticator, 'token'):
            return self.authenticator.token
        if callable(self.authenticator):
            return self.authenticator()
        if isinstance(self.authenticator, Mapping) and 'token' in self.authenticator:
            return self.authenticator['token']

    def __init__(self, authenticator=None) -> None:
        self.authenticator = authenticator

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        token = self.token
        if token is not None:
            r.headers["Authorization"] = f"Bearer {token}"
        return r


def api_client(url, token=None):
    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    client = rframe.RestClient(
        url,
        headers=headers,
    )
    return client
