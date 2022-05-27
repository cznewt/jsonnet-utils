import json
import re
import os
import glob
import _jsonnet
import logging
import subprocess
from .prometheus_rule import metrics_rules
from .utils import search_prometheus_metrics

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

GRAFONNET_INCLUDES = """
    local grafana = import 'grafonnet/grafana.libsonnet';
    local dashboard = grafana.dashboard;
    local row = grafana.row;
    local prometheus = grafana.prometheus;
    local template = grafana.template;
    local graphPanel = grafana.graphPanel;"""

GRAFONNET_DASHBOARD = """
    dashboard.new(\n{}, tags={})"""

GRAFONNET_ROW = """
    row.new()"""

GRAFONNET_GRAPH_PANEL = """
    .addPanel(
      graphPanel.new(
        '{}',
        datasource='$datasource',
        span={},
        format='{}',
        stack={},
        min=0,
      )
    )"""

GRAFONNET_SINGLESTAT_PANEL = """
    .addPanel(
      singlestat.new(
        '{}',
        datasource='$datasource',
        span={},
        format='{}',
        valueName='current',
      )
    )"""

GRAFONNET_PROMETHEUS_TARGET = """
    .addTarget(
      prometheus.target(
        |||
          {}
        ||| % $._config,
        legendFormat='',
      )
    )"""

GRAFONNET_INFLUXDB_TARGET = """
    .addTarget(
      influxdb.target(
        |||
          {}
        ||| % $._config,
        alias='{}',
      )
    )"""

GRAPH_BUILDER_DASHBOARD = """
    g.dashboard({}, tags={})
"""


def print_dashboard_info(dashboard):
    output = [""]
    output.append(
        "\n### Dashboard {} (schema: {}, {})\n".format(
            dashboard.get("title", "N/A"),
            dashboard.get("schemaVersion", "N/A"),
            dashboard.get("_filename"),
        )
    )
    # output.append("variables:")
    # output.append(
    #    "    count: {}".format(len(dashboard.get("templating", {}).get("list", [])))
    # )
    # output.append("    items:")
    # for variable in dashboard.get("templating", {}).get("list", []):
    #    output.append("    - {} ({})".format(variable["name"], variable["type"]))
    # output.append("  panels:")
    # output.append("    count: {}".format(len(dashboard.get("_panels", []))))
    # output.append("    items:")

    for panel in dashboard.get("_panels", []):
        output.append("\n#### Panel {} ({})\n".format(panel["title"], panel["type"]))
        for target in panel["targets"]:
            if "expr" in target:
                output.append(
                    "* **{}**: {}".format(
                        "**, **".join(search_prometheus_metrics(target["expr"])),
                        target["expr"],
                    )
                )
    return "\n".join(output)


def print_dashboard_metrics(dashboard):
    output = [""]
    metrics = []
    output.append("{}:".format(dashboard.get("_filename")))
    for panel in dashboard.get("_panels", []):
        for target in panel.get("targets", []):
            if "expr" in target:
                queries = search_prometheus_metrics(target["expr"])
                metrics += queries
    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append("- {}".format(metric))
    #  for line in output:
    #      print(line)
    return final_metrics


def data_dashboard_metrics(dashboard):
    metrics = []
    data = {"nodes": [], "links": []}
    data["nodes"].append(
        {
            "id": dashboard.get("_filename"),
            "type": "grafana-dashboard",
            "name": dashboard.get("_filename"),
            "sources": [],
            "targets": [],
        }
    )
    data["links"].append(
        {"source": dashboard.get("_filename"), "target": "output", "value": 10}
    )
    panels = dashboard.get("_panels", [])
    if len(panels) == 0:
        panels = dashboard.get("panels", [])
    for panel in panels:
        for target in panel.get("targets", []):
            if "expr" in target:
                queries = search_prometheus_metrics(target["expr"])
                metrics += queries
    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        data["links"].append(
            {"source": metric, "target": dashboard.get("_filename"), "value": 10}
        )
    return data


def convert_dashboard_jsonnet(dashboard, format, source_path, build_path):
    dashboard_lines = []
    if format == "grafonnet":
        dashboard_lines.append(GRAFONNET_INCLUDES)
        dashboard_lines.append("{\ngrafanaDashboards+:: {")
        dashboard_lines.append("'{}':".format(dashboard["_filename"]))
        dashboard_lines.append(
            GRAFONNET_DASHBOARD.format('"' + dashboard.get("title", "N/A") + '"', [])
        )
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable["type"] == "query":
                if variable["multi"]:
                    multi = "Multi"
                else:
                    multi = ""
                dashboard_lines.append(
                    "\n.add{}Template('{}', '{}', 'instance')".format(
                        multi, variable["name"], variable["query"]
                    )
                )
        for row in dashboard.get("rows", []):
            dashboard_lines.append(".addRow(")
            dashboard_lines.append("row.new()")
            for panel in row.get("panels", []):
                if panel["type"] == "singlestat":
                    dashboard_lines.append(
                        GRAFONNET_SINGLESTAT_PANEL.format(
                            panel["title"], panel["span"], panel["format"]
                        )
                    )
                if panel["type"] == "graph":
                    dashboard_lines.append(
                        GRAFONNET_GRAPH_PANEL.format(
                            panel["title"],
                            panel["span"],
                            panel["yaxes"][0]["format"],
                            panel["stack"],
                        )
                    )
                for target in panel.get("targets", []):
                    if "expr" in target:
                        dashboard_lines.append(
                            GRAFONNET_PROMETHEUS_TARGET.format(target["expr"])
                        )
            dashboard_lines.append(")")

        dashboard_lines.append("}\n}")
    else:
        dashboard_body = GRAPH_BUILDER_DASHBOARD.format(
            '"' + dashboard.get("title", "N/A") + '"', []
        )
        for variable in dashboard.get("templating", {}).get("list", []):
            if variable["type"] == "query":
                if variable["multi"]:
                    multi = "Multi"
                else:
                    multi = ""
                dashboard_body += "\n.add{}Template('{}', '{}', 'instance')".format(
                    multi, variable["name"], variable["query"]
                )

    dashboard_str = "\n".join(dashboard_lines)

    if build_path == "":
        print("JSONNET:\n{}".format(dashboard_str))
        print("JSON:\n{}".format(_jsonnet.evaluate_snippet("snippet", dashboard_str)))
    else:
        build_file = (
            build_path + "/" + dashboard["_filename"].replace(".json", ".jsonnet")
        )
        with open(build_file, "w") as the_file:
            the_file.write(dashboard_str)
        output = (
            subprocess.Popen(
                "jsonnet fmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i "
                + build_file,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            .stdout.read()
            .decode("utf-8")
        )
        if "ERROR" in output:
            logging.info(
                "Error `{}` converting dashboard `{}/{}` to `{}`".format(
                    output, source_path, dashboard["_filename"], build_file
                )
            )
        else:
            logging.info(
                "Converted dashboard `{}/{}` to `{}` ({} format)".format(
                    source_path, dashboard["_filename"], build_file, format
                )
            )

    return dashboard_str


def parse_dashboard(board_file):
    with open(board_file) as f:
        dashboard = json.load(f)
    panels = []
    for row in dashboard.get("panels", []):
        for panel in row.get("panels", []):
            panels.append(panel)

    for row in dashboard.get("rows", []):
        for panel in row.get("panels", []):
            panels.append(panel)
            for subpanel in panel.get("panels", []):
                panels.append(subpanel)
    dashboard["_filename"] = os.path.basename(board_file)
    dashboard["_panels"] = panels
    return dashboard


def info_dashboards(path):
    board_output = []
    board_files = glob.glob("{}/*.json".format(path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        board_output.append(print_dashboard_info(dashboard))
    if len(board_files) == 0:
        logging.error("No dashboards found at given path!")

    return "\n".join(board_output)


def metrics_dashboards(path, output="console"):
    board_files = glob.glob("{}/*.json".format(path))
    if output == "console":
        sum_metrics = []
        for board_file in board_files:
            dashboard = parse_dashboard(board_file)
            board_metrics = print_dashboard_metrics(dashboard)
            sum_metrics += board_metrics
        if len(board_files) > 0:
            sum_metrics = sorted(list(set(sum_metrics)))
        else:
            logging.error("No dashboards found at given path!")
    else:
        sum_metrics = {"nodes": [], "links": []}
        for board_file in board_files:
            dashboard = parse_dashboard(board_file)
            board_metrics = data_dashboard_metrics(dashboard)
            sum_metrics["nodes"] += board_metrics["nodes"]
            sum_metrics["links"] += board_metrics["links"]

    return sum_metrics


def metrics_all(dashboard_path, rules_path, output):
    if output == "json":
        metrics = {"nodes": [], "links": []}
        metrics["nodes"].append(
            {
                "id": "input",
                "type": "input",
                "name": "input",
                "sources": [],
                "targets": [],
            }
        )
        metrics["nodes"].append(
            {
                "id": "output",
                "type": "output",
                "name": "output",
                "sources": [],
                "targets": [],
            }
        )
        board_metrics = metrics_dashboards(dashboard_path, output)
        metrics["nodes"] += board_metrics["nodes"]
        metrics["links"] += board_metrics["links"]
        rule_metrics = metrics_rules(rules_path, output)
        metrics["nodes"] += rule_metrics["nodes"]
        metrics["links"] += rule_metrics["links"]
        metric_names = []
        new_metric_names = []
        final_map = {}
        final_nodes = []
        final_links = []
        for node in metrics["nodes"]:
            metric_names.append(node["id"])
        input_links = []
        for link in metrics["links"]:
            if link["source"] not in metric_names:
                metric_names.append(link["source"])
                metrics["nodes"].append(
                    {
                        "id": link["source"],
                        "type": "prometheus-metric",
                        "name": link["source"],
                        "sources": [],
                        "targets": [],
                    }
                )
                input_links.append(
                    {"source": "input", "target": link["source"], "value": 10}
                )
        metrics["links"] += input_links
        i = 0
        for node in metrics["nodes"]:
            if node["id"] not in new_metric_names:
                final_nodes.append(node)
                final_map[node["id"]] = i
                i += 1
            new_metric_names.append(node["id"])
        metrics["nodes"] = final_nodes
        """
        for link in metrics['links']:
            link['source'] = final_map[link['source']]
            link['target'] = final_map[link['target']]
            final_links.append(link)
        metrics['links'] = final_links
        """
        for link in metrics["links"]:
            metrics["nodes"][final_map[link["source"]]]["sources"].append(
                link["target"]
            )
            metrics["nodes"][final_map[link["target"]]]["targets"].append(
                link["source"]
            )

        for node in metrics["nodes"]:
            logging.debug(
                "{} {} S: {} T: {}".format(
                    node["type"], node["id"], node["sources"], node["targets"]
                )
            )

        return json.dumps(metrics)
    else:
        out = []
        metrics = metrics_rules(rules_path) + metrics_dashboards(dashboard_path)
        sum_metrics = sorted(list(set(metrics)))
        out.append("")
        out.append("combined-metrics:")
        for metric in sum_metrics:
            out.append("- {}".format(metric))
        for line in out:
            print(line)


def convert_dashboards(source_path, build_path, format, layout):
    board_files = glob.glob("{}/*.json".format(source_path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        convert_dashboard_jsonnet(dashboard, format, source_path, build_path)

    if len(board_files) == 0:
        logging.error("No dashboards found at given path!")


def test_dashboards(path):
    board_files = glob.glob("{}/*.json".format(path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        logging.info("Testing dashboard `{}` ... OK".format(dashboard["_filename"]))
    if len(board_files) == 0:
        logging.error("No dashboards found at given path!")
