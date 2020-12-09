

from jsonnet_utils.prometheus_rule import search_prometheus_metrics

from pytablewriter import MarkdownTableWriter
from math import floor

import logging

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ])

test_queries = [
    '''
        ALERTS{alertstate="firing", cluster="cluster"}
    ''',
    '(count(ALERTS{alertstate="firing", cluster_name="cluster}) by (cluster_name)) or (sum(up{job="federate", cluster_name="cluster}) by (cluster_name) - 1)',
    '1 - sum(:node_memory_MemFreeCachedBuffers:sum{cluster_name=~"cluster}) / sum(:node_memory_MemTotal:sum{cluster_name=~"cluster})',
    'node:node_cpu_utilisation:avg1m{cluster_name="cluster"} * node:node_num_cpu:sum{cluster_name="cluster"} / scalar(sum(node:node_num_cpu:sum{cluster_name="cluster"}))',
    'sum(cluster_services:healthy_total{cluster_name=~"^gc[0-9].*"}) by (cluster_name)',
    'max(node_load1{job="kubernetes-node-exporter", cluster_name="cluster", instance="instance"})',
    '''
        sum(
          label_replace(
            namespace_pod_name_container_name:container_cpu_usage_seconds_total:sum_rate{label="cluster", namespace="$namespace"},
            "pod", "$1", "pod_name", "(.*)"
          ) * on(namespace,pod) group_left(workload, workload_type) mixin_pod_workload{label="cluster", namespace="namespace", workload="workload", workload_type="type"}
        ) by (pod)
    ''',
]

for test_query in test_queries:
    logging.info('-----------------------------')
    logging.info('Testing query: {}'.format(test_query))
    metrics = search_prometheus_metrics(test_query, True)
    logging.info('Found metrics: {}'.format(' '.join(metrics)))
