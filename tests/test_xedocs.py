#!/usr/bin/env python
"""Tests for `xedocs` package."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

import xedocs
from xedocs import cli

HAVE_UTILIX = False
try:
    import utilix
    HAVE_UTILIX = True
except ImportError:
    pass


@pytest.mark.skipif(not HAVE_UTILIX, reason='utilix not installed')
def test_straxen_database():
    from xedocs.databases import straxen_db

    db = straxen_db()
    assert db is not None


def test_find_schema():
    from xedocs.schemas import XeDoc

    for name, schema in XeDoc._XEDOCS.items():

        found_schema = xedocs.find_schema(name)
        assert schema is found_schema

        found_schema = xedocs.find_schema(schema.__name__)
        assert schema is found_schema

        found_schema = xedocs.find_schema(schema)
        assert schema is found_schema


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
