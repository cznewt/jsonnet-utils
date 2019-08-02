
import yaml

def parse_yaml(yaml_file):
    with open(yaml_file) as f:
        try:
            data = yaml.load(f, Loader=yaml.FullLoader)
        except AttributeError:
            data = yaml.load(f)
    return data