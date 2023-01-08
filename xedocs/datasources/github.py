
from xedocs import settings
from xedocs.schemas import XeDoc


def github_source(schema: XeDoc):
    return settings.github_url_for_schema(schema)
