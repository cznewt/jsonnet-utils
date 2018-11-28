from setuptools import setup, find_packages

setup(
    name='jsonnet_utils',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'jsonnet',
    ],
    entry_points='''
        [console_scripts]
        jsonnet-grafana-dashboards-convert=jsonnet_utils.cli:dashboards_convert
        jsonnet-grafana-dashboards-info=jsonnet_utils.cli:dashboards_info
        jsonnet-grafana-dashboards-test=jsonnet_utils.cli:dashboards_test
    ''',
)
