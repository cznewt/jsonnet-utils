
import json
import yaml
import re
import os
import glob
import _jsonnet
import logging
import subprocess


PROMETHEUS_RECORD_RULES = '''
{
  prometheusRules+:: {
    groups+: [
        {}
    ]
  }
}'''


def parse_rules(rules_file):
    with open(rules_file) as f:
        if rules_file.endswith('.yaml') or rules_file.endswith('.yml'):
            rule = yaml.load(f)
        else:
            rule = json.load(f)
    rule['_filename'] = os.path.basename(rules_file)
    return rule


def search_prometheus_metrics(orig_query, debug=False):
    keywords = ['(', ')', '-', '/', '*', '+', '-', '!',
                ',', '>', '<', '=', '^', '.', '"']
    final_keywords = ['', '0', 'sum', 'bool', 'rate', 'irate', 'sort',
                      'count', 'avg', 'histogram_quantile', 'round',
                      'max', 'min', 'time', 'topk', 'changes',
                      'label_replace', 'delta', 'predict_linear',
                      'increase', 'scalar', 'e', 'or', 'absent']
    if debug:
        logging.info(query)
    query = orig_query.replace("\n", ' ')
    query = re.sub(r'[0-9]+e[0-9]+', '', query)
    query = re.sub(r'\{.*\}', '', query)
    query = re.sub(r'\[.*\]', '', query)
    query = re.sub(r'\".*\"', '', query)
    if debug:
        logging.info(query)
    query = re.sub(r'by \((\w|,| )+\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'by\((\w|,| )+\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'on \((\w|,| )+\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'on\((\w|,| )+\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'without \(.*\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'without\(.*\)', '', query, flags=re.IGNORECASE)
    if debug:
        logging.info(query)
    for keyword in keywords:
        query = query.replace(keyword, ' ')
    query = re.sub(r'[0-9]+ ', ' ', query)
    query = re.sub(r' [0-9]+', ' ', query)
    final_queries = []
    query = query.replace("(", ' ')
    raw_queries = query.split(' ')
    for raw_query in raw_queries:
        #if raw_query.strip() == '0':
        #    logging.info(orig_query)
        if raw_query.lower().strip() not in final_keywords:
            final_queries.append(raw_query.lower().strip())
    return final_queries


def convert_rule_jsonnet(rule, source_path, build_path):
    rule_lines = []

    for group in rule['groups']:
        rule_lines.append(json.dumps(group, indent=2))

    rule_str = "{\nprometheusAlerts+:: {\ngroups+: [\n" + \
        ',\n'.join(rule_lines) + "\n]\n}\n}"

    if build_path == '':
        print(rule_str)
    else:
        filename = rule['_filename'].replace(
            '.yml', '.jsonnet').replace('.yaml', '.jsonnet')
        build_file = build_path + '/' + filename
        with open(build_file, 'w') as the_file:
            the_file.write(rule_str)
        output = subprocess.Popen("jsonnet fmt -n 2 --max-blank-lines 2 --string-style s --comment-style s -i " + build_file,
                                  shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.read().decode("utf-8")
        if 'ERROR' in output:
            logging.info('Error `{}` converting rules file `{}/{}` to `{}`.'.format(
                output, source_path, rule['_filename'], build_file))
        else:
            logging.info('Converted rules file `{}/{}` to `{}`.'.format(
                source_path, rule['_filename'], build_file))

    return rule_str


def print_rule_info(rule):
    output = ['']
    output.append('{}:'.format(rule.get('_filename')))
    output.append('  groups:')
    for group in rule.get('groups', []):
        output.append('  - {}:'.format(
            group['name']))
        for rul in group.get('rules', []):
            if 'record' in rul:
                kind = 'record'
            else:
                kind = 'alert'
            if 'expr' in rul:
                output.append(
                    '    - {} ({})'.format(rul['expr'].replace('\n', ''), kind))
    for line in output:
        print(line)


def print_rule_metrics(rule):
    output = ['']
    metrics = []
    output.append('{}:'.format(rule.get('_filename')))
    for group in rule.get('groups', []):
        for rul in group.get('rules', []):
            if 'expr' in rul:
                queries = search_prometheus_metrics(
                    rul['expr'].replace('\n', ' '))
                # output.append('  - {}'.format(rul['expr']))
                metrics += queries

    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append('- {}'.format(metric))
    for line in output:
        print(line)
    return final_metrics


def data_rule_metrics(rule):
    data = {'nodes': [], 'links': []}
    for group in rule.get('groups', []):
        for rul in group.get('rules', []):
            metrics = []
            if 'record' in rul:
                name = rul['record']
                kind = 'prometheus-record'
            else:
                name = rul['alert']
                kind = 'prometheus-alert'
            data['nodes'].append({
                'id': name,
                'type': kind,
                'name': name,
                'sources': [],
                'targets': [],
            })
            data['links'].append({
                'source': name,
                'target': 'output',
                'value': 10,
            })
            if 'expr' in rul:
                #if name == 'node:node_disk_utilisation:avg_irate':
                queries = search_prometheus_metrics(
                    rul['expr'].replace('\n', ' '))
                # output.append('  - {}'.format(rul['expr']))
                metrics += list(set(queries))
            for metric in metrics:
                data['links'].append({
                    'source': metric,
                    'target': name,
                    'value': 10,
                })
    return data

    final_metrics = sorted(list(set(metrics)))
    for metric in final_metrics:
        output.append('- {}'.format(metric))
    for line in output:
        print(line)
    return final_metrics


def info_rules(path):
    rule_files = glob.glob('{}/*.yml'.format(path)) + \
        glob.glob('{}/*.yaml'.format(path))
    for rule_file in rule_files:
        rules = parse_rules(rule_file)
        print_rule_info(rules)
    if len(rule_files) == 0:
        logging.error('No rule definitions found at given path!')


def metrics_rules(path, output='console'):
    rule_files = glob.glob('{}/*.yml'.format(path)) + \
        glob.glob('{}/*.yaml'.format(path))
    if output == "console":
        metrics = []
        for rule_file in rule_files:
            rules = parse_rules(rule_file)
            metrics += print_rule_metrics(rules)
        if len(rule_files) == 0:
            logging.error('No rules found at given path!')
    else:
        metrics = {'nodes': [], 'links': []}
        for rule_file in rule_files:
            rules = parse_rules(rule_file)
            board_metrics = data_rule_metrics(rules)
            metrics['nodes'] += board_metrics['nodes']
            metrics['links'] += board_metrics['links']
    return metrics


def convert_rules(source_path, build_path):
    rule_files = glob.glob('{}/*.yml'.format(source_path)) + \
        glob.glob('{}/*.yaml'.format(source_path))
    for rule_file in rule_files:
        rule = parse_rules(rule_file)
        convert_rule_jsonnet(rule, source_path, build_path)

    if len(rule_files) == 0:
        logging.error('No rules found at given path!')
