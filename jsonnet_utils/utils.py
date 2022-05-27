import yaml
import re
import logging

split_keywords = [
    " / ",
    " + ",
    " * ",
    " - ",
    ">",
    "<",
    " or ",
    " and ",
    " group_left ",
    " group_right ",
    " AND ",
    " OR ",
    " GROUP_LEFT ",
    " GROUP_RIGHT ",
]
keywords = [
    "-",
    "/",
    "(",
    ")",
    "!",
    ",",
    "^",
    ".",
    '"',
    "=",
    "*",
    "+",
    ">",
    "<",
    " instance ",
    " job ",
    " type ",
    " url ",
    "?:",
]
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
    "count_values",
    "count_over_time",
    "avg",
    "avg_over_time",
    "histogram_quantile",
    "quantile_over_time",
    "stddev",
    "stddev_over_time",
    "stdvar",
    "stdvar_over_time",
    "round",
    "max",
    "max_over_time",
    "min",
    "min_over_time",
    "time",
    "topk",
    "bottomk",
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
    "offset",
    "s",
    "m",
    "d",
    "w",
    "y",
    "json",
    "$filter",
    "|",
]


def parse_yaml(yaml_file):
    with open(yaml_file) as f:
        try:
            data = yaml.load(f, Loader=yaml.FullLoader)
        except AttributeError:
            data = yaml.load(f)
    return data


def split_by_keyword(query, split_keywords, level=0):
    if level < len(split_keywords):
        new_query = []
        for item in query:
            new_query = new_query + item.split(split_keywords[level])
        return split_by_keyword(new_query, split_keywords, level + 1)

    else:
        return query


def clean_comments(query):
    lines = query.splitlines()
    output_lines = []
    for line in lines:
        line = line.strip()
        if not line.startswith("#"):
            output_lines.append(line)
    return " ".join(output_lines)


def search_prometheus_metrics(orig_query):
    query = clean_comments(orig_query)
    print(query)
    query = re.sub(r"[0-9]+e[0-9]+", "", query)
    query = query.replace(" [0-9]+ ", "")
    query = re.sub(
        r"group_left \((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_left\((\w|,| )+\)", " group_left ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_right \((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE
    )
    query = re.sub(
        r"group_right\((\w|,| )+\)", " group_right ", query, flags=re.IGNORECASE
    )

    subqueries = split_by_keyword([query], split_keywords, 0)

    logging.debug("Step 1: {}".format(query))
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

    logging.debug("Step 2: {}".format(query))
    for keyword in keywords:
        query = query.replace(keyword, " ")
    query = re.sub(r" [0-9]+ ", " ", query)
    query = re.sub(r" [0-9]+", " ", query)
    query = re.sub(r"^[0-9]+$", " ", query)
    query = query.replace("(", " ")
    final_queries = []

    logging.debug("Step 3: {}".format(query))
    raw_queries = query.split(" ")
    for raw_query in raw_queries:
        if raw_query.lower().strip() not in final_keywords:
            raw_query = re.sub(r"^[0-9]+$", " ", raw_query)
            if raw_query.strip() != "":
                final_queries.append(raw_query.strip())

    output = list(set(final_queries))

    logging.debug("Parsed query: {}".format(orig_query))
    logging.debug("Found metrics: {}".format(output))
    return output
