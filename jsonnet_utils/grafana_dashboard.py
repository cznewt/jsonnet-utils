
import json
import re
import os
import glob
import _jsonnet
import logging
import subprocess

logging.basicConfig(
    format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ])

GRAFONNET_INCLUDES = '''
    local grafana = import 'grafonnet/grafana.libsonnet';
    local dashboard = grafana.dashboard;
    local row = grafana.row;
    local prometheus = grafana.prometheus;
    local template = grafana.template;
    local graphPanel = grafana.graphPanel;'''

GRAFONNET_DASHBOARD = '''
    dashboard.new(\n{}, tags={})'''

GRAFONNET_ROW = '''
    row.new()'''

GRAFONNET_GRAPH_PANEL = '''
    .addPanel(
      graphPanel.new(
        '{}',
        datasource='$datasource',
        span={},
        format='{}',
        stack={},
        min=0,
      )
    )'''

GRAFONNET_SINGLESTAT_PANEL = '''
    .addPanel(
      singlestat.new(
        '{}',
        datasource='$datasource',
        span={},
        format='{}',
        valueName='current',
      )
    )'''

GRAFONNET_PROMETHEUS_TARGET = '''
    .addTarget(
      prometheus.target(
        |||
          {}
        ||| % $._config,
        legendFormat='',
      )
    )'''

GRAFONNET_INFLUXDB_TARGET = '''
    .addTarget(
      influxdb.target(
        |||
          {}
        ||| % $._config,
        alias='{}',
      )
    )'''

GRAPH_BUILDER_DASHBOARD = '''
    g.dashboard({}, tags={})
'''


def print_dashboard_info(dashboard):
    output = ['']
    output.append('{}:'.format(dashboard.get('_filename')))
    output.append('  title: {}'.format(dashboard.get('title', 'N/A')))
    output.append('  schema-version: {}'.format(
        dashboard.get('schemaVersion', 'N/A')))
    output.append('  variables:')
    output.append('    count: {}'.format(
        len(dashboard.get('templating', {}).get('list', []))))
    output.append('    items:')
    for variable in dashboard.get('templating', {}).get('list', []):
        output.append('    - {} ({})'.format(
            variable['name'], variable['type']))
    output.append('  panels:')
    output.append('    count: {}'.format(
        len(dashboard.get('_panels', []))))
    output.append('    items:')
    for panel in dashboard.get('_panels', []):
        output.append('    - {} ({})'.format(panel['title'], panel['type']))
    for line in output:
        print(line)


def serch_prometheus_metrics(query):
    keywords = ['(', ')', '-', '/', '*', '+', '-',
                ',', '>', '<', '=', '^', '.', '"']
    final_keywords = ['', 'sum', 'bool', 'rate', 'irate', 'count', 'avg', 'histogram_quantile',
                      'max', 'min', 'time', 'topk', 'changes', 'label_replace']
    query = query.replace("\n", ' ')
    query = re.sub(r'[0-9]+e[0-9]+', '', query)
    query = re.sub(r'\{.*\}', '', query)
    query = re.sub(r'\[.*\]', '', query)
    query = re.sub(r'\".*\"', '', query)
    query = re.sub(r'by \(.*\)', '', query)
    query = re.sub(r'without \(.*\)', '', query)
    for keyword in keywords:
        query = query.replace(keyword, ' ')
    query = re.sub(r'[0-9]+ ', ' ', query)
    query = re.sub(r' [0-9]+', ' ', query)
    final_queries = []
    query = query.replace("(", ' ')
    raw_queries = query.split(' ')
    for raw_query in raw_queries:
        if raw_query.lower() not in final_keywords:
            final_queries.append(raw_query)
    return final_queries


def print_dashboard_metrics(dashboard):
    output = ['']
    metrics = []
    output.append('{}:'.format(dashboard.get('_filename')))
    #output.append('  expressions:')
    for panel in dashboard.get('_panels', []):
        for target in panel.get('targets', []):
            if 'expr' in target:
                queries = serch_prometheus_metrics(
                    target['expr'].replace('\n', ' '))
                #output.append('  - {}'.format(target['expr']))
                metrics += queries

    output.append('  metrics:')
    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append('  - {}'.format(metric))
    for line in output:
        print(line)
    return final_metrics


def convert_dashboard_jsonnet(dashboard, format, source_path, build_path):
    dashboard_lines = []
    if format == 'grafonnet':
        dashboard_lines.append(GRAFONNET_INCLUDES)
        dashboard_lines.append("{\ngrafanaDashboards+:: {")
        dashboard_lines.append("'{}':".format(dashboard['_filename']))
        dashboard_lines.append(GRAFONNET_DASHBOARD.format(
            '"' + dashboard.get('title', 'N/A') + '"', []))
        for variable in dashboard.get('templating', {}).get('list', []):
            if variable['type'] == 'query':
                if variable['multi']:
                    multi = 'Multi'
                else:
                    multi = ''
                dashboard_lines.append("\n.add{}Template('{}', '{}', 'instance')".format(
                    multi, variable['name'], variable['query']))
        for row in dashboard.get('rows', []):
            dashboard_lines.append('.addRow(')
            dashboard_lines.append('row.new()')
            for panel in row.get('panels', []):
                if panel['type'] == 'singlestat':
                    dashboard_lines.append(GRAFONNET_SINGLESTAT_PANEL.format(
                        panel['title'],
                        panel['span'],
                        panel['format'],
                    ))
                if panel['type'] == 'graph':
                    dashboard_lines.append(GRAFONNET_GRAPH_PANEL.format(
                        panel['title'],
                        panel['span'],
                        panel['yaxes'][0]['format'],
                        panel['stack'],
                    ))
                for target in panel.get('targets', []):
                    if 'expr' in target:
                        dashboard_lines.append(GRAFONNET_PROMETHEUS_TARGET.format(
                            target['expr'],
                        ))
            dashboard_lines.append(')')

        dashboard_lines.append("}\n}")
    else:
        dashboard_body = GRAPH_BUILDER_DASHBOARD.format(
            '"' + dashboard.get('title', 'N/A') + '"', [])
        for variable in dashboard.get('templating', {}).get('list', []):
            if variable['type'] == 'query':
                if variable['multi']:
                    multi = 'Multi'
                else:
                    multi = ''
                dashboard_body += "\n.add{}Template('{}', '{}', 'instance')".format(
                    multi, variable['name'], variable['query'])

    dashboard_str = '\n'.join(dashboard_lines)

    if build_path == '':
        print('JSONNET:\n{}'.format(dashboard_str))
        print('JSON:\n{}'.format(_jsonnet.evaluate_snippet(
            "snippet", dashboard_str)))
    else:
        build_file = build_path + '/' + \
            dashboard['_filename'].replace('.json', '.jsonnet')
        with open(build_file, 'w') as the_file:
            the_file.write(dashboard_str)
        output = subprocess.Popen("jsonnet fmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i " + build_file,
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().decode("utf-8")
        if 'ERROR' in output:
            logging.info('Error `{}` converting dashboard `{}/{}` to `{}`'.format(
                output, source_path, dashboard['_filename'], build_file))
        else:
            logging.info('Converted dashboard `{}/{}` to `{}` ({} format)'.format(
                source_path, dashboard['_filename'], build_file, format))

    return dashboard_str


def parse_dashboard(board_file):
    with open(board_file) as f:
        dashboard = json.load(f)
    panels = []
    for row in dashboard['rows']:
        for panel in row['panels']:
            panels.append(panel)
    dashboard['_filename'] = os.path.basename(board_file)
    dashboard['_panels'] = panels
    return dashboard


def info_dashboards(path):
    board_files = glob.glob('{}/*.json'.format(path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        print_dashboard_info(dashboard)
    if len(board_files) == 0:
        logging.error('No dashboards found at given path!')


def metrics_dashboards(path):
    board_files = glob.glob('{}/*.json'.format(path))
    sum_metrics = []
    output = []
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        board_metrics = print_dashboard_metrics(dashboard)
        sum_metrics += board_metrics
    if len(board_files) > 0:
        sum_metrics = sorted(list(set(sum_metrics)))
        output.append('')
        output.append('complete-set:')
        for metric in sum_metrics:
            output.append('- {}'.format(metric))
        for line in output:
            print(line)
    else:
        logging.error('No dashboards found at given path!')


def convert_dashboards(source_path, build_path, format, layout):
    board_files = glob.glob('{}/*.json'.format(source_path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        convert_dashboard_jsonnet(dashboard, format, source_path, build_path)

    if len(board_files) == 0:
        logging.error('No dashboards found at given path!')


def test_dashboards(path):
    board_files = glob.glob('{}/*.json'.format(path))
    for board_file in board_files:
        dashboard = parse_dashboard(board_file)
        logging.info('Testing dashboard `{}` ... OK'.format(
            dashboard['_filename']))
    if len(board_files) == 0:
        logging.error('No dashboards found at given path!')
