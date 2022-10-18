#!/usr/bin/env python
"""Tests for `xedocs` package."""
# pylint: disable=redefined-outer-name

import pytest
from click.testing import CliRunner

from xedocs import cli


def test_staging_context():
    from xedocs.contexts import staging_db

    ctx = staging_db()
    assert ctx is not None
    ctx = staging_db(by_category=False)
    assert ctx is not None


def test_production_context():
    from xedocs.contexts import production_db

    ctx = production_db()
    assert ctx is not None
    ctx = production_db(by_category=False)
    assert ctx is not None


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
