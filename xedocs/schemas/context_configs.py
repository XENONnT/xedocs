from typing import Dict

import rframe

from .base_schemas import VersionedXeDoc
from .plugin_lineages import PluginLineage


class ContextLineage(VersionedXeDoc):
    _ALIAS = "context_lineages"

    strax: str = rframe.Index()
    straxen: str = rframe.Index()

    lineage_hashes: Dict[str, str]

    def load_config(self, datasource=None):
        hashes = list(self.lineage_hashes.values())
        docs = PluginLineage.find(datasource, lineage_hash=hashes)
        config = {}
        for doc in docs:
            config.update(doc.config)
        return config
