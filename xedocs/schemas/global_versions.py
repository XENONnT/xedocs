import rframe

from .base_schemas import VersionedXeDoc


class GlobalVersion(VersionedXeDoc):
    _NAME = "global_versions"

    strax_version: str = rframe.Index()
    straxen_version: str = rframe.Index()

    @classmethod
    def get_global_config(cls, version, datasource=None, names=None, extra_labels=None):
        """Build a context config from the given global version."""
        import straxen

        if extra_labels is None:
            extra_labels = dict(run_id="plugin.run_id")
        refs = cls.find(datasource, version=version, alias=names)
        config = {}
        for ref in refs:
            url = ref.url_config
            if extra_labels is not None:
                url = straxen.URLConfig.format_url_kwargs(url, **extra_labels)
            config[ref.alias] = url
        return config
