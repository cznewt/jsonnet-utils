
=============
jsonnet-utils
=============

Utility scripts to work with JSONNET and monitoring mixins.

Commands
========

At the moment just a few utilities to work with Grafana dashboards

jsonnet-utils-grafana-convert
----------------------------------

Convert JSON dashboards to JSONNET format.

Usage: ``jsonnet-utils-grafana-convert [OPTIONS]``

Options:

--source-path TEXT  Path to search for the source JSON dashboards.
--build-path TEXT   Path to save converted JSONNET dashboards, none to print to console.
--format TEXT       Format of the dashboard: `grafonnet` or `grafana-builder`.
--layout TEXT       Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).

Example usage:

.. code::

    jsonnet-utils-grafana-convert --source-path=./tests/data --build-path ./build
    Searching path `./tests/data` for JSON dashboards to convert ...
    Converted dashboard `./tests/data/server-single_rev3.json` to `./build/server-single_rev3.jsonnet`
    Converted dashboard `./tests/data/prometheus-redis_rev1.json` to `./build/prometheus-redis_rev1.jsonnet`


jsonnet-utils-grafana-info
--------------------------

Get info from Grafana JSON dashboards.

Usage: ``jsonnet-utils-grafana-info [OPTIONS]``

Options:

--path TEXT  Path to search for the source JSON dashboards.

Example usage:

.. code::

    jsonnet-utils-grafana-info --path=./tests/data
    Searching path `./tests/data` for JSON dashboards for detailed info ...
    
    server-single_rev3.json:
      title: Linux host
      schema-version: 14
      variables:
        count: 1
        items:
        - host (query)
      panels:
        count: 7
        items:
        - DISK partitions (graph)
        - Processes (graph)
        - swap (graph)
        - CPU usage (graph)
        - RAM (graph)
        - IP traffic (graph)
        - system: load (5m) (graph)
    
    prometheus-redis_rev1.json:
      title: Prometheus Redis
      schema-version: 12
      variables:
        count: 1
        items:
        - addr (query)
      panels:
        count: 11
        items:
        - Uptime (singlestat)
        - Clients (singlestat)
        - Memory Usage (singlestat)
        - Commands Executed / sec (graph)
        - Hits / Misses per Sec (graph)
        - Total Memory Usage (graph)
        - Network I/O (graph)
        - Total Items per DB (graph)
        - Expiring vs Not-Expiring Keys (graph)
        - Expired / Evicted (graph)
        - Command Calls / sec (graph)


jsonnet-utils-grafana-test
--------------------------

Test JSONNET formatted dashboards.

Usage: ``jsonnet-utils-grafana-test [OPTIONS]``


Options:

--path TEXT    Path to search for the source JSON dashboards.
--scheme TEXT  Scheme version of the dashboard: `16` is the current.
--layout TEXT  Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).

Example usage:

.. code::

    jsonnet-utils-grafana-test --path=./tests/data
    2018-11-28 00:50:02,298 [INFO ]  Searching path `./tests/data` for JSON dashboards to test ...
    2018-11-28 00:50:02,298 [INFO ]  Testing dashboard `server-single_rev3.json` ... OK
    2018-11-28 00:50:02,299 [INFO ]  Testing dashboard `prometheus-redis_rev1.json` ... OK

jsonnet-utils-grafana-metrics
-----------------------------

Get Prometheus metric names from Grafana JSON dashboard targets.

Usage: jsonnet-utils-grafana-metrics [OPTIONS]

Options:

--path TEXT  Path to search for the source JSON dashboards.

Example usage:

.. code::

    jsonnet-utils-grafana-metrics --path=./tests/source
    Searching path `./tests/source` for JSON dashboards for targets ...
    
    prometheus-redis_rev1.json:
      panels:
      - panel :Uptime
        targets:
        - expr: redis_uptime_in_seconds{addr="$addr"}
      - panel :Clients
        targets:
        - expr: redis_connected_clients{addr="$addr"}
      - panel :Memory Usage
        targets:
        - expr: 100 * (redis_memory_used_bytes{addr=~"$addr"}  / redis_config_maxmemory{addr=~"$addr"} )
      - panel :Commands Executed / sec
        targets:
        - expr: rate(redis_commands_processed_total{addr=~"$addr"}[5m])
      - panel :Hits / Misses per Sec
        targets:
        - expr: irate(redis_keyspace_hits_total{addr="$addr"}[5m])
        - expr: irate(redis_keyspace_misses_total{addr="$addr"}[5m])
      - panel :Total Memory Usage
        targets:
        - expr: redis_memory_used_bytes{addr=~"$addr"}
        - expr: redis_config_maxmemory{addr=~"$addr"}
      - panel :Network I/O
        targets:
        - expr: rate(redis_net_input_bytes_total{addr="$addr"}[5m])
        - expr: rate(redis_net_output_bytes_total{addr="$addr"}[5m])
      - panel :Total Items per DB
        targets:
        - expr: sum (redis_db_keys{addr=~"$addr"}) by (db)
      - panel :Expiring vs Not-Expiring Keys
        targets:
        - expr: sum (redis_db_keys{addr=~"$addr"}) - sum (redis_db_keys_expiring{addr=~"$addr"})
        - expr: sum (redis_db_keys_expiring{addr=~"$addr"})
      - panel :Expired / Evicted
        targets:
        - expr: sum(rate(redis_expired_keys_total{addr=~"$addr"}[5m])) by (addr)
        - expr: sum(rate(redis_evicted_keys_total{addr=~"$addr"}[5m])) by (addr)
      - panel :Command Calls / sec
        targets:
        - expr: topk(5, irate(redis_command_call_duration_seconds_count{addr=~"$addr"} [1m]))
      metrics:
      - redis_command_call_duration_seconds_count
      - redis_commands_processed_total
      - redis_config_maxmemory
      - redis_connected_clients
      - redis_db_keys
      - redis_db_keys_expiring
      - redis_evicted_keys_total
      - redis_expired_keys_total
      - redis_keyspace_hits_total
      - redis_keyspace_misses_total
      - redis_memory_used_bytes
      - redis_net_input_bytes_total
      - redis_net_output_bytes_total
      - redis_uptime_in_seconds

Roadmap
=======

* Convert row based layout to grid layout
* Support for Prometheus, InfluxDB and ElasticSearch datasources
* Testing of JSONNET sources and built resources
