
=============
jsonnet-utils
=============

Utility scripts to work with JSONNET and monitoring resource mixins.

* Grafana dashboards
* Prometheus alert and record rules

Commands
========

At the moment just a few utilities to work with Grafana dashboard and Prometheus
alarm definition mixins.

jsonnet-utils-prometheus-convert
--------------------------------

Convert YAML rules to JSONNET format.

Usage: ``jsonnet-utils-prometheus-convert [OPTIONS]``

Options:

--source-path TEXT  Path to search for the source YAML rules.
--build-path TEXT   Path to save converted JSONNET dashboards, none to print to console.

Example usage:

.. code::

    jsonnet-utils-prometheus-convert --source-path=../data/alarms --build-path=./build
    Searching path `../data/alarms` for YAML rule definitions to convert ...
    Converted rules file `../data/alarms/alarms.yml` to `./build/alarms.jsonnet`.

Example result JSONNET definition:

.. code::

    {                                                                                                                                                                                  
      prometheusAlerts+:: {                                                                                                                                                                                                                                                                                           
        groups+: [                                                                                                                                                 
          {                                                                                                                                                                                                                                                                                   
            name: 'kubernetes-apps',                                                                                                      
            rules: [                                                                                                                                                                                                                               
              {                                                                                                                                                                                                               
                alert: 'KubePodCrashLooping',                                                                                                  
                annotations: {                                                                                                                                    
                  message: 'Pod {{ $labels.namespace }}/{{ $labels.pod }} ({{ $labels.container }}) is restarting {{ printf "%.2f" $value }} times / 5 minutes.',
                },                                                                                                                                                                     
                expr: 'rate(kube_pod_container_status_restarts_total{kubernetes_name="kube-state-metrics"}[15m]) * 60 * 5 > 0\n',                                                                                                                                                                                     
                'for': '1h',                                                                                                                                       
                labels: {                                                                                                                                                                                                                                                                     
                  severity: 'critical',                                                                                                                                                                                                            
                },                                                                                                                                 
              },                                                                                                                                                                                                                                  
              {                                                                                                                                                                                                                                    
                alert: 'KubePodNotReady',                                                                            
                annotations: {                                                                                                                                 
                  message: 'Pod {{ $labels.namespace }}/{{ $labels.pod }} has been in a non-ready state for longer than an hour.',
                },                                                                                                                                                                                                                                                                          
                expr: 'sum by (namespace, pod) (kube_pod_status_phase{kubernetes_name="kube-state-metrics", phase=~"Pending|Unknown"}) > 0\n',
                'for': '1h',                                                                                                                                                                              
                labels: {                  
                  severity: 'critical',                                                                                                                             
                },                                                                                                      
              },                                                                                                                                                              
            ],                                                                                                                                                                
          },
        ]
      }
    }
    

jsonnet-utils-grafana-convert
-----------------------------

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

Example result JSONNET definition:

.. code::

local grafana = import 'grafonnet/grafana.libsonnet';
    local dashboard = grafana.dashboard;
    local row = grafana.row;    
    local prometheus = grafana.prometheus;                                                                
    local template = grafana.template;                      
    local graphPanel = grafana.graphPanel;
    {                           
      grafanaDashboards+:: {    
        'prometheus-redis_rev1.json':
                                                        
          dashboard.new(        
            'Prometheus Redis', tags=[]   
          )                                     
                                         
          .addTemplate('addr', 'label_values(redis_connected_clients, addr)', 'instance')
          .addRow(             
            row.new()                                                                          
                                
            .addPanel(                                 
              singlestat.new(   
                'Uptime',       
                datasource='$datasource',
                span=1,         
                format='s',                                              
                valueName='current',                                                              
              )
            )
    
            .addTarget(
              prometheus.target(
                |||
                  redis_uptime_in_seconds{addr="$addr"}
                ||| % $._config,
                legendFormat='',
              )
            )
    
            .addPanel(
              singlestat.new(
                'Clients',
                datasource='$datasource',
                span=1,
                format='none',
                valueName='current',
              )
            )
    
            .addTarget(
              prometheus.target(
                |||
                  redis_connected_clients{addr="$addr"}
                ||| % $._config,
                legendFormat='',
              )
            )  
          )
      }
    }


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
