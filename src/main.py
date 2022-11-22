import load_data
import pg_store
import argparse

if __name__== "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config",default = "params.yml")
    args.add_argument("--schema",default = "schema.yml" )
    parsed_args = args.parse_args()
    load_data.load_and_preprocess(config_path=parsed_args.config)
    pg_store.postgress_actions(config_path=parsed_args.config,schema_path = parsed_args.schema)