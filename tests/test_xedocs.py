#!/usr/bin/env python
"""Tests for `xedocs` package."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

import xedocs
from xedocs import cli


def test_analyst_context():
    from xedocs.contexts import analyst_db

    ctx = analyst_db()
    assert ctx is not None
    ctx = analyst_db(by_category=False)
    assert ctx is not None


def test_straxen_context():
    from xedocs.contexts import straxen_db

    ctx = straxen_db()
    assert ctx is not None
    ctx = straxen_db(by_category=False)
    assert ctx is not None


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
