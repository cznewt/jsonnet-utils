from jsonnet_utils.utils import search_prometheus_metrics

from math import floor

import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)

test_queries = [
    {
        "query": """
          ALERTS{alertstate="firing", cluster="cluster"}
        """,
        "result": ["ALERTS"],
    },
    {
        "query": '(count(ALERTS{alertstate="firing", cluster_name="cluster}) by (cluster_name)) or (sum(up{job="federate", cluster_name="cluster}) by (cluster_name) - 1)',
        "result": ["ALERTS", "up"],
    },
    {
        "query": '1 - sum(:node_memory_MemFreeCachedBuffers:sum{cluster_name=~"cluster}) / sum(:node_memory_MemTotal:sum{cluster_name=~"cluster})',
        "result": [
            ":node_memory_MemTotal:sum",
            ":node_memory_MemFreeCachedBuffers:sum",
        ],
    },
    {
        "query": 'node:node_cpu_utilisation:avg1m{cluster_name="cluster"} * node:node_num_cpu:sum{cluster_name="cluster"} / scalar(sum(node:node_num_cpu:sum{cluster_name="cluster"}))',
        "result": [
            "node:node_cpu_utilisation:avg1m",
            "node:node_num_cpu:sum",
            "node:node_num_cpu:sum",
        ],
    },
    {
        "query": 'sum(cluster_services:healthy_total{cluster_name=~"^gc[0-9].*"}) by (cluster_name)',
        "result": ["cluster_services:healthy_total"],
    },
    {
        "query": 'max(node_load1{job="kubernetes-node-exporter", cluster_name="cluster", instance="instance"})',
        "result": ["node_load1"],
    },
    {
        "query": """
          # test bla bla bla
          sum(
            label_replace(
              namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate{label="cluster", namespace="$namespace"},
              "pod", "$1", "pod_name", "(.*)"
            ) * on(namespace,pod) group_left(workload, workload_type) mixin_pod_workload{label="cluster", namespace="namespace", workload="workload", workload_type="type"}
          ) by (pod)
        """,
        "result": [
            "mixin_pod_workload",
            "namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate",
        ],
    },
]

for test_query in test_queries:
    logging.info("Testing ...\n {}".format(test_query["query"]))
    metrics = search_prometheus_metrics(test_query["query"])
    if set(metrics) == set(test_query["result"]):
        logging.info("OK, found: {}\n".format(set(metrics)))
    else:
        logging.info(
            "Failed, found: {}, expected: {}\n".format(
                set(metrics), set(test_query["result"])
            )
        )
