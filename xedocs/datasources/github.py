
from xedocs import settings
from xedocs.schemas import XeDoc


def github_source(schema: XeDoc):
    return settings.GITHUB_URL.format(name=schema._ALIAS)
