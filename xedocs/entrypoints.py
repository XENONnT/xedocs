# Entrypoint loading logic
# Can be used to register schemas and data sources.
# The nice optimization of the different import attempts
# was copied from the hypothesis package
# https://github.com/HypothesisWorks/hypothesis/blob/master/hypothesis-python/src/hypothesis/entry_points.py
import warnings

try:
    # We prefer to use importlib.metadata, or the backport on Python <= 3.7,
    # because it's much faster than pkg_resources (200ms import time speedup).
    try:
        from importlib import metadata as importlib_metadata
    except ImportError:
        import importlib_metadata  # type: ignore  # mypy thinks this is a redefinition

    def get_entry_points(name="xedocs"):
        try:
            eps = importlib_metadata.entry_points(group=name)
        except TypeError:
            # Load-time selection requires Python >= 3.10 or importlib_metadata >= 3.6,
            # so we'll retain this fallback logic for some time to come.  See also
            # https://importlib-metadata.readthedocs.io/en/latest/using.html
            eps = importlib_metadata.entry_points().get(name, [])
        yield from eps

except ImportError:
    # But if we're not on Python >= 3.8 and the importlib_metadata backport
    # is not installed, we fall back to pkg_resources anyway.
    try:
        import pkg_resources
    except ImportError:
        import warnings

        warnings.warn(
            "Under Python <= 3.7, xedocs requires either the importlib_metadata "
            "or setuptools package in order to load plugins via entrypoints.",
        )

        def get_entry_points(name):
            yield from ()

    else:

        def get_entry_points(name="xedocs"):
            yield from pkg_resources.iter_entry_points(name)


def load_entry_points(name):
    hooks = {}
    for entry in get_entry_points(name):  # pragma: no cover
        try:
            hook = entry.load()
            if callable(hook):
                hooks[entry.name] = hook
        except Exception as e:
            warnings.warn(f"Could not import entrypoint {entry.name}. \n {e}")
    return hooks
