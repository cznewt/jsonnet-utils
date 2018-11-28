
import json
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
        rule = json.load(f)
    rule['_filename'] = os.path.basename(rules_file)
    return rule


def search_prometheus_metrics(query):
    keywords = ['(', ')', '-', '/', '*', '+', '-',
                ',', '>', '<', '=', '^', '.', '"']
    final_keywords = ['', 'sum', 'bool', 'rate', 'irate',
                      'count', 'avg', 'histogram_quantile',
                      'max', 'min', 'time', 'topk', 'changes',
                      'label_replace', 'delta', 'predict_linear',
                      'increase', 'scalar', 'e']
    query = query.replace("\n", ' ')
    query = re.sub(r'[0-9]+e[0-9]+', '', query)
    query = re.sub(r'\{.*\}', '', query)
    query = re.sub(r'\[.*\]', '', query)
    query = re.sub(r'\".*\"', '', query)
    query = re.sub(r'by \(.*\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'by\(.*\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'without \(.*\)', '', query, flags=re.IGNORECASE)
    query = re.sub(r'without\(.*\)', '', query, flags=re.IGNORECASE)
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
            logging.info('Error `{}` converting rules file `{}/{}` to `{}`'.format(
                output, source_path, rule['_filename'], build_file))
        else:
            logging.info('Converted rules file `{}/{}` to `{}` ({} format)'.format(
                source_path, rule['_filename'], build_file, format))

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


def info_rules(path):
    rule_files = glob.glob('{}/*.yml'.format(path)) + \
        glob.glob('{}/*.yaml'.format(path))
    for rule_file in rule_files:
        rules = parse_rules(rule_file)
        print_rule_info(rules)
    if len(rule_files) == 0:
        logging.error('No rule definitions found at given path!')


def metrics_rules(path):
    rule_files = glob.glob('{}/*.yml'.format(path)) + \
        glob.glob('{}/*.yaml'.format(path))
    metrics = []
    for rule_file in rule_files:
        rules = parse_rules(rule_file)
        metrics += print_rule_metrics(rules)
    if len(rule_files) == 0:
        logging.error('No rules found at given path!')
    return metrics


def convert_rules(source_path, build_path):
    rule_files = glob.glob('{}/*.yml'.format(source_path)) + \
        glob.glob('{}/*.yaml'.format(source_path))
    for rule_file in rule_files:
        rule = parse_rules(rule_file)
        convert_rule_jsonnet(rule, source_path, build_path)

    if len(rule_files) == 0:
        logging.error('No rules found at given path!')
