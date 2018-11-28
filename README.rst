
=============
jsonnet-utils
=============

Utility scripts to work with JSONNET and monitoring mixins.

Commands
========

At the moment just a few utilities to work with Grafana dashboards

jsonnet-grafana-dashboards-convert
----------------------------------

Usage: jsonnet-grafana-dashboards-convert [OPTIONS]

  Convert JSON dashboards to JSONNET format.

Options:

* --source-path TEXT  Path to search for the source JSON dashboards.
* --build-path TEXT   Path to save converted JSONNET dashboards, none to print to console.
* --format TEXT       Format of the dashboard: `grafonnet` or `grafana-builder`.
* --layout TEXT       Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).

Example usage:

.. code::

    jsonnet-grafana-dashboards-convert --source-path=./tests/data --build-path ./build
    2018-11-28 00:53:04,537 [INFO ]  Searching path `./tests/data` for JSON dashboards to convert ...
    2018-11-28 00:53:04,541 [INFO ]  Converted dashboard `./tests/data/server-single_rev3.json` to `./build/server-single_rev3.jsonnet`
    2018-11-28 00:53:04,546 [INFO ]  Converted dashboard `./tests/data/prometheus-redis_rev1.json` to `./build/prometheus-redis_rev1.jsonnet`


jsonnet-grafana-dashboards-info
-------------------------------

Usage: jsonnet-grafana-dashboards-info [OPTIONS]

  Get info from Grafana JSON dashboards.

Options:

* --path TEXT  Path to search for the source JSON dashboards.

Example usage:

.. code::

    jsonnet-grafana-dashboards-info --path=./tests/data
    2018-11-28 00:51:16,472 [INFO ]  Searching path `./tests/data` for JSON dashboards for detailed info ...
    2018-11-28 00:51:16,472 [INFO ]
    2018-11-28 00:51:16,472 [INFO ]  server-single_rev3.json:
    2018-11-28 00:51:16,472 [INFO ]    title: Linux host
    2018-11-28 00:51:16,472 [INFO ]    schema-version: 14
    2018-11-28 00:51:16,472 [INFO ]    variables:
    2018-11-28 00:51:16,473 [INFO ]      count: 1
    2018-11-28 00:51:16,473 [INFO ]      items:
    2018-11-28 00:51:16,473 [INFO ]      - host (query)
    2018-11-28 00:51:16,473 [INFO ]    panels:
    2018-11-28 00:51:16,473 [INFO ]      count: 7
    2018-11-28 00:51:16,473 [INFO ]      items:
    2018-11-28 00:51:16,473 [INFO ]      - DISK partitions (graph)
    2018-11-28 00:51:16,473 [INFO ]      - Processes (graph)
    2018-11-28 00:51:16,473 [INFO ]      - swap (graph)
    2018-11-28 00:51:16,473 [INFO ]      - CPU usage (graph)
    2018-11-28 00:51:16,473 [INFO ]      - RAM (graph)
    2018-11-28 00:51:16,473 [INFO ]      - IP traffic (graph)
    2018-11-28 00:51:16,473 [INFO ]      - system: load (5m) (graph)
    2018-11-28 00:51:16,473 [INFO ]
    2018-11-28 00:51:16,473 [INFO ]  prometheus-redis_rev1.json:
    2018-11-28 00:51:16,473 [INFO ]    title: Prometheus Redis
    2018-11-28 00:51:16,473 [INFO ]    schema-version: 12
    2018-11-28 00:51:16,474 [INFO ]    variables:
    2018-11-28 00:51:16,474 [INFO ]      count: 1
    2018-11-28 00:51:16,474 [INFO ]      items:
    2018-11-28 00:51:16,474 [INFO ]      - addr (query)
    2018-11-28 00:51:16,474 [INFO ]    panels:
    2018-11-28 00:51:16,474 [INFO ]      count: 11
    2018-11-28 00:51:16,474 [INFO ]      items:
    2018-11-28 00:51:16,474 [INFO ]      - Uptime (singlestat)
    2018-11-28 00:51:16,474 [INFO ]      - Clients (singlestat)
    2018-11-28 00:51:16,474 [INFO ]      - Memory Usage (singlestat)
    2018-11-28 00:51:16,474 [INFO ]      - Commands Executed / sec (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Hits / Misses per Sec (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Total Memory Usage (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Network I/O (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Total Items per DB (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Expiring vs Not-Expiring Keys (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Expired / Evicted (graph)
    2018-11-28 00:51:16,474 [INFO ]      - Command Calls / sec (graph)


jsonnet-grafana-dashboards-test
-------------------------------

Usage: jsonnet-grafana-dashboards-test [OPTIONS]

  Test JSONNET formatted dashboards.

Options:

* --path TEXT    Path to search for the source JSON dashboards.
* --scheme TEXT  Scheme version of the dashboard: `16` is the current.
* --layout TEXT  Format of the dashboard: `normal` (scheme 14) , `grid` (scheme 16).

Example usage:

.. code::

    jsonnet-grafana-dashboards-test --path=./tests/data
    2018-11-28 00:50:02,298 [INFO ]  Searching path `./tests/data` for JSON dashboards to test ...
    2018-11-28 00:50:02,298 [INFO ]  Testing dashboard `server-single_rev3.json` ... OK
    2018-11-28 00:50:02,299 [INFO ]  Testing dashboard `prometheus-redis_rev1.json` ... OK


Roadmap
=======

* Convert row based layout to grid layout
* Support for Prometheus, InfluxDB and ElasticSearch datasources
* Testing of JSONNET sources and built resources
