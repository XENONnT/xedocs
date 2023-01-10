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
    from xedocs.schemas import PmtGain

    schema = xedocs.find_schema("pmt_gains")

    assert schema is PmtGain

    schema = xedocs.find_schema(PmtGain)

    assert schema is PmtGain


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
