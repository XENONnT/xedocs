import os
from warnings import warn

import rframe

CACHE = {}

API_URL = "http://api.xedocs.yossisprojects.com"


def api_client(name, token=None, readonly=True):
    cache_key = f"api_token_readonly_{readonly}"

    if token is None:
        token = CACHE.get(cache_key, None)

    if token is None:
        token = os.environ.get("XEDOCS_API_TOKEN", None)

    if token is None:
        try:
            import xeauth

            xetoken = xeauth.cmt_login(scope="write:all")
            token = xetoken.access_token
        except ImportError:
            pass

    headers = {}
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"
        CACHE[cache_key] = token

    client = rframe.RestClient(
        f"{API_URL}/{name}",
        headers=headers,
    )
    return client
