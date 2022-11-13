import rframe
from requests import PreparedRequest
from requests.auth import AuthBase


class ApiAuth(AuthBase):
    authenticator = None

    def __init__(self, authenticator=None) -> None:
        self.authenticator = authenticator

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        if self.authenticator is not None:
            r.headers["Authorization"] = f"Bearer {self.authenticator.token}"
        return r


def api_client(url, token=None, authenticator=None, headers=None, client=None):
    headers = headers if headers is not None else {}

    if token is not None:
        auth = f"Bearer {token}"
    elif authenticator is not None:
        auth = ApiAuth(authenticator)
    else:
        auth = None
    client = rframe.RestClient(
        url,
        headers=headers,
        client=client,
        auth=auth,
    )
    return client
