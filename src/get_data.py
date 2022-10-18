import argparse
import yaml
from utils.common_util import get_latest_file

def read_params(config_path):
    with open(config_path) as yaml_file:
        config = yaml.safe_load(yaml_file)
    return config

def get_data(config_path):
    config = read_params(config_path)
    source_data_path = get_latest_file(config,'xls')
    with open(source_data_path , 'r') as f:
        contents = f.readlines()
    return contents

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config",default = "../params.yml")
    parsed_args = args.parse_args()
    data = get_data(config_path=parsed_args.config)






