#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import click
import logging
from .grafana_dashboard import (
    convert_dashboards,
    info_dashboards,
    test_dashboards,
    metrics_dashboards,
    metrics_all,
)
from .prometheus_rule import convert_rules, metrics_rules, info_rules

from .utils import is_debug_active

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)


def set_logger():
    debug = is_debug_active()
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.info("Setting logging to DEBUG level...")
    else:
        logging.getLogger().setLevel(logging.INFO)
        logging.info("Setting logging to INFO level...")


@click.command()
@click.option(
    "--source-path",
    default="./source",
    help="Path to search for the source JSON dashboards.",
)
@click.option(
    "--build-path",
    default="",
    help="Path to save converted JSONNET dashboards, none to print to console.",
)
@click.option(
    "--format",
    default="grafonnet",
    help="Format of the dashboard: `grafonnet` or `grafana-builder`.",
)
@click.option(
    "--layout",
    default="rows",
    help="Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).",
)
def dashboard_convert(source_path, build_path, format, layout):
    """Convert JSON dashboards to JSONNET format."""
    logging.info(
        "Searching path `{}` for JSON dashboards to convert ...".format(source_path)
    )
    set_logger()
    convert_dashboards(source_path, build_path, format, layout)


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the source JSON dashboards."
)
@click.option(
    "--scheme",
    default="16",
    help="Scheme version of the dashboard: `16` is the current.",
)
@click.option(
    "--layout",
    default="rows",
    help="Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).",
)
def dashboard_test(path, scheme, layout):
    """Test JSONNET formatted dashboards."""
    logging.info("Searching path `{}` for JSON dashboards...".format(path))
    set_logger()
    test_dashboards(path)


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the source JSON dashboards."
)
def dashboard_info(path):
    """Get info from Grafana JSON dashboards."""
    logging.info(
        "Searching path `{}` for JSON dashboards...".format(path)
    )
    print(info_dashboards(path))


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the JSON dashboards."
)
def dashboard_metrics(path):
    """Get metric names from Grafana JSON dashboard targets."""
    logging.info("Searching path `{}` for JSON dashboards...".format(path))
    set_logger()
    metrics_dashboards(path)


@click.command()
@click.option(
    "--dashboard-path",
    default="./data/grafana",
    help="Path to search for the Grafana JSON dashboards.",
)
@click.option(
    "--rules-path",
    default="./data/prometheus",
    help="Path to search for the Prometheus YAML rules.",
)
@click.option("--output", default="console", help="Type of output [console/json]")
def all_metrics(dashboard_path, rules_path, output):
    """Get metric names from Grafana JSON dashboard targets and Prometheus rules."""
    logging.info(
        "Searching path `{}` for JSON dashboards for metrics ...".format(dashboard_path)
    )
    logging.info(
        "Searching path `{}` for YAML rules for metrics ...".format(rules_path)
    )
    set_logger()
    metrics_all(dashboard_path, rules_path, output)


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the YAML rule definions."
)
def rule_info(path):
    """Get detailed info from Prometheus rule targets."""
    logging.info(
        "Searching path `{}` for YAML rule definitions for detailed info ...".format(
            path
        )
    )
    set_logger()
    info_rules(path)


@click.command()
@click.option(
    "--path", default="./data", help="Path to search for the YAML rule definions."
)
def rule_metrics(path):
    """Get metric names from Prometheus rule targets."""
    logging.info(
        "Searching path `{}` for YAML rule definitions for metrics ...".format(path)
    )
    set_logger()
    metrics_rules(path)


@click.command()
@click.option(
    "--source-path",
    default="./source",
    help="Path to search for the source YAML rule files.",
)
@click.option(
    "--build-path",
    default="",
    help="Path to save converted JSONNET rules, none to print to console.",
)
def rule_convert(source_path, build_path):
    """Convert Prometheus rule definitions to JSONNET format."""
    logging.info(
        "Searching path `{}` for YAML rule definitions to convert ...".format(
            source_path
        )
    )
    set_logger()
    convert_rules(source_path, build_path)
