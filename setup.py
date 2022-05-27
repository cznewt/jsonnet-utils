from setuptools import setup, find_packages

setup(
    name='jsonnet_utils',
    version='0.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'jsonnet',
    ],
    entry_points='''
        [console_scripts]
        jsonnet-utils-all-metrics=jsonnet_utils.cli:all_metrics
        jsonnet-utils-grafana-metrics=jsonnet_utils.cli:dashboard_metrics
        jsonnet-utils-prometheus-metrics=jsonnet_utils.cli:rule_metrics
        jsonnet-utils-grafana-convert=jsonnet_utils.cli:dashboard_convert
        jsonnet-utils-prometheus-convert=jsonnet_utils.cli:rule_convert
        jsonnet-utils-grafana-info=jsonnet_utils.cli:dashboard_info
        jsonnet-utils-prometheus-info=jsonnet_utils.cli:rule_info
        jsonnet-utils-grafana-test=jsonnet_utils.cli:dashboard_test
    ''',
)
