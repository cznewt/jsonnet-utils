import json
import yaml
import re
import os
import glob
import _jsonnet
import logging
import subprocess

from .utils import parse_yaml

PROMETHEUS_RECORD_RULES = """
{
  prometheusRules+:: {
    groups+: [
        {}
    ]
  }
}"""


def parse_rules(rules_file):
    with open(rules_file) as f:
        if rules_file.endswith(".yaml") or rules_file.endswith(".yml"):
            rule = parse_yaml(rules_file)
        else:
            rule = json.load(f)
    rule["_filename"] = os.path.basename(rules_file)
    return rule


def split_by_keyword(query, split_keywords, level=0):
    if level < len(split_keywords):
        new_query = []
        for item in query:
            new_query = new_query + item.split(split_keywords[level])
        return split_by_keyword(new_query, split_keywords, level + 1)

    else:
        return query


def search_prometheus_metrics(orig_query, debug=False):
    split_keywords = [" / ", " + ", " * ", " - ", "\n" ">", "<", " or ", " and ", " group_left ", " group_right ", " AND ", " OR ", " GROUP_LEFT ", " GROUP_RIGHT "]
    keywords = ["-", "/", "(", ")", "!", ",", "^", ".", '"', "=", "*", "+", ">", "<", " instance ", " job ", " type ", " url ", "?:"]
    final_keywords = [
        "0",
        "sum",
        "bool",
        "rate",
        "irate",
        "sort",
        "sort_desc",
        "sqrt",
        "round",
        "floor",
        "resets",
        "count",
        "count_over_time",
        "avg",
        "avg_over_time",
        "histogram_quantile",
        "quantile_over_time",
        "stddev_over_time",
        "stdvar_over_time",
        "round",
        "max",
        "max_over_time",
        "min",
        "min_over_time",
        "time",
        "topk",
        "changes",
        "clamp_max",
        "clamp_min",
        "label_replace",
        "label_join",
        "increase",
        "idelta",
        "delta",
        "deriv",
        "predict_linear",
        "holt_winters",
        "increase",
        "scalar",
        "vector",
        "e",
        "exp",
        "abs",
        "ceil",
        "absent",
        "inf",
        "year",
        "timestamp",
        "time",
        "month",
        "minute",
        "hour",
        "day_of_month",
        "day_of_week",
        "days_in_month",
        "log10",
        "log2",
        "ln",
    ]
    query = orig_query
     # .replace("\n", " ")
    query = re.sub(r"[0-9]+e[0-9]+", "", query)
    query = query.replace(' [0-9]+ ', '')
    query = re.sub(r"group_left \((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE)
    query = re.sub(r"group_left\((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE)
    query = re.sub(r"group_right \((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE)
    query = re.sub(r"group_right\((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE)

    subqueries = split_by_keyword([query], split_keywords, 0)
    if debug:
        logging.info("Step 1: {}".format(query))
    subquery_output = []
    for subquery in subqueries:
        subquery = re.sub(r"\{.*\}", "", subquery)
        subquery = re.sub(r"\[.*\]", "", subquery)
        subquery = re.sub(r"\".*\"", "", subquery)

        subquery = re.sub(r"by \((\w|,| )+\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"by\((\w|,| )+\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"on \((\w|,| )+\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"on\((\w|,| )+\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"without \(.*\)", "", subquery, flags=re.IGNORECASE)
        subquery = re.sub(r"without\(.*\)", "", subquery, flags=re.IGNORECASE)
        subquery_output.append(subquery)
    query = " ".join(subquery_output)

    if debug:
        logging.info("Step 2: {}".format(query))
    for keyword in keywords:
        query = query.replace(keyword, " ")
    query = re.sub(r" [0-9]+ ", " ", query)
    query = re.sub(r" [0-9]+", " ", query)
    query = re.sub(r"^[0-9]+$", " ", query)
    query = query.replace("(", " ")
    final_queries = []
    if debug:
        logging.info("Step 3: {}".format(query))
    raw_queries = query.split(" ")
    for raw_query in raw_queries:
        if raw_query.lower().strip() not in final_keywords:
            raw_query = re.sub(r"^[0-9]+$", " ", raw_query)
            if raw_query.strip() != "":
                final_queries.append(raw_query.strip())


    output = list(set(final_queries))
    logging.info('Parsed query: ', orig_query)
    logging.info('Found metrics: ', output)
    return output

def convert_rule_jsonnet(rule, source_path, build_path):
    rule_lines = []

    for group in rule["groups"]:
        rule_lines.append(json.dumps(group, indent=2))

    rule_str = (
        "{\nprometheusAlerts+:: {\ngroups+: [\n" + ",\n".join(rule_lines) + "\n]\n}\n}"
    )

    if build_path == "":
        print(rule_str)
    else:
        filename = (
            rule["_filename"].replace(".yml", ".jsonnet").replace(".yaml", ".jsonnet")
        )
        build_file = build_path + "/" + filename
        with open(build_file, "w") as the_file:
            the_file.write(rule_str)
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
                "Error `{}` converting rules file `{}/{}` to `{}`.".format(
                    output, source_path, rule["_filename"], build_file
                )
            )
        else:
            logging.info(
                "Converted rules file `{}/{}` to `{}`.".format(
                    source_path, rule["_filename"], build_file
                )
            )

    return rule_str


def print_rule_info(rule):
    output = [""]
    output.append("### File {}".format(rule.get("_filename")))
    # output.append("  groups:")
    for group in rule.get("groups", []):
        output.append("\n#### Group {}\n".format(group["name"]))

        for rul in group.get("rules", []):
            if "record" in rul:
                kind = "record"
            else:
                kind = "alert"
            if "expr" in rul:
                output.append(
                    "- **{}**: ({})".format(
                        "**, **".join(
                            search_prometheus_metrics(rul["expr"].replace("\n", ""))
                        ),
                        rul["expr"].replace("\n", ""),
                        kind,
                    )
                )
    return "\n".join(output)


def print_rule_metrics(rule):
    output = [""]
    metrics = []
    output.append("{}:".format(rule.get("_filename")))
    for group in rule.get("groups", []):
        for rul in group.get("rules", []):
            if "expr" in rul:
                queries = search_prometheus_metrics(rul["expr"].replace("\n", " "))
                # output.append('  - {}'.format(rul['expr']))
                metrics += queries

    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append("- {}".format(metric))
    for line in output:
        print(line)
    return final_metrics


def data_rule_metrics(rule):
    data = {"nodes": [], "links": []}
    for group in rule.get("groups", []):
        for rul in group.get("rules", []):
            metrics = []
            if "record" in rul:
                name = rul["record"]
                kind = "prometheus-record"
            else:
                name = rul["alert"]
                kind = "prometheus-alert"
            data["nodes"].append(
                {"id": name, "type": kind, "name": name, "sources": [], "targets": []}
            )
            data["links"].append({"source": name, "target": "output", "value": 10})
            if "expr" in rul:
                # if name == 'node:node_disk_utilisation:avg_irate':
                queries = search_prometheus_metrics(rul["expr"].replace("\n", " "))
                # output.append('  - {}'.format(rul['expr']))
                metrics += list(set(queries))
            for metric in metrics:
                data["links"].append({"source": metric, "target": name, "value": 10})
    return data

    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append("- {}".format(metric))
    for line in output:
        print(line)
    return final_metrics


def info_rules(path):
    rule_output = []
    rule_files = glob.glob("{}/*.yml".format(path)) + glob.glob(
        "{}/*.yaml".format(path)
    )
    for rule_file in rule_files:
        rules = parse_rules(rule_file)
        rule_output.append(print_rule_info(rules))
    if len(rule_files) == 0:
        logging.error("No rule definitions found at given path!")

    return "\n".join(rule_output)


def metrics_rules(path, output="console"):
    rule_files = glob.glob("{}/*.yml".format(path)) + glob.glob(
        "{}/*.yaml".format(path)
    )
    if output == "console":
        metrics = []
        for rule_file in rule_files:
            rules = parse_rules(rule_file)
            metrics += print_rule_metrics(rules)
        if len(rule_files) == 0:
            logging.error("No rules found at given path!")
    else:
        metrics = {"nodes": [], "links": []}
        for rule_file in rule_files:
            rules = parse_rules(rule_file)
            board_metrics = data_rule_metrics(rules)
            metrics["nodes"] += board_metrics["nodes"]
            metrics["links"] += board_metrics["links"]
    return metrics


def convert_rules(source_path, build_path):
    rule_files = glob.glob("{}/*.yml".format(source_path)) + glob.glob(
        "{}/*.yaml".format(source_path)
    )
    for rule_file in rule_files:
        rule = parse_rules(rule_file)
        convert_rule_jsonnet(rule, source_path, build_path)

    if len(rule_files) == 0:
        logging.error("No rules found at given path!")

