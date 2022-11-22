import re
import os
import argparse
import pandas as pd
from glob import glob
from get_data import read_params
from get_data import read_params
from utils.common_util import get_latest_file
from postgress_connections.create_connection import connect,create_table,insert_table

def pg_preprocess(config):

    # read data
    acc_data = pd.read_csv(get_latest_file(config,'csv'))

    # drop null values from data
    acc_data.dropna(subset=['Txn_Date'],axis=0,inplace=True)

    # create date and year column from Txn_Date
    acc_data['Txn_Date']  = pd.to_datetime(acc_data['Txn_Date'])
    acc_data['Txn_Year'] = acc_data['Txn_Date'].dt.year
    acc_data['Txn_Month'] = acc_data['Txn_Date'].dt.strftime('%b')

    # clean all amounts (from string to float)
    acc_data['Balance'] = acc_data['Balance'].apply(lambda x: float(x.replace(',','').strip()) if (len(x.strip())>=1) else float(x.replace(str(x),'0')))
    acc_data['Debit'] = acc_data['Debit'].apply(lambda x: float(x.replace(',','').strip()) if (len(x.strip())>=1) else float(x.replace(str(x),'0')))
    acc_data['Credit'] = acc_data['Credit'].apply(lambda x: float(x.replace(',','').strip()) if (len(x.strip())>=1) else float(x.replace(str(x),'0')))

    # get the customer name and bank name
    acc_data['cust_name'] = acc_data['Description'].apply(lambda x: re.split(r'/|\*',x)[3] if len(re.split(r'/|\*',x))>3 else 'Not_aval' )
    acc_data['cust_bank_name'] = acc_data['Description'].apply(lambda x: re.split(r'/|\*',x)[4] if len(re.split(r'/|\*',x))>=5 else 'Not_aval' )

    # columns going to use for feature data
    pg_acc_data = acc_data[['Txn_Date','Txn_Year','Txn_Month','cust_name','cust_bank_name','Debit','Credit','Balance']]

    return pg_acc_data

def get_table_info(config,dataframe):
    table_name = []
    table_path = []
    for year in dataframe['Txn_Year'].unique():
        yearly_data = dataframe[dataframe['Txn_Year'] == year]
        for month in yearly_data['Txn_Month'].unique():
            table_name.append(f'{month.lower()}{str(year)}')
            monthly_data =  yearly_data[yearly_data['Txn_Month']==month]
            path = os.path.join(config['get_utility']['feature_data_path'],f'{month.lower()}{str(year)}.csv')
            table_path.append(f'opt/source_data/{month.lower()}{str(year)}.csv')
            monthly_data.to_csv(path,index=False,header =False)
    return table_name,table_path

def postgress_actions(config_path,schema_path):
    config = read_params(config_path)
    schema = read_params(schema_path)
    
    # read feature data
    pg_acc_data = pg_preprocess(config)
    tab_names,paths = get_table_info(config,pg_acc_data)
    _,cur = connect()

    create_table(tab_names,schema['table_schema'],cur)
    import docker
    import subprocess
    client = docker.from_env()
    # pg_container = client.containers.list(filters={'name':'account_analyzer-postges-1'})
    pg_container = client.containers.list()
    print('containers -->',pg_container[0].id)
    for path,name in zip(paths,tab_names):
#         p = subprocess.call(["docker", "cp", f"Data_files/feature_data/target_data/{name}.csv", f"{pg_container[0].id}:opt/source_data"],shell=True)
        command = f'''psql -U postgres -d monthlyaccsummary -c "\copy {name} from {path} delimiter ',' csv"'''
        subprocess.call(["docker" ,"exec" ,"t" ,f"{pg_container[0].id}" ,"/bin/bash"])
        print(pg_container[0].exec_run("ls"))
        print(pg_container[0].exec_run("ls opt"))  
        print(pg_container[0].exec_run("ls opt/source_data"))  
        result = pg_container[0].exec_run(command)
#         print(p)
        print(result)

    # print(tab_names)
    # for path,name in zip(paths,tab_names):
    #     path = os.path.normpath(path)
    #     # print(glob(path))
    #     insert_table(path,name,cur)




if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("--config",default = "params.yml")
    args.add_argument("--schema",default = "schema.yml" )
    parsed_args = args.parse_args()
    data = postgress_actions(config_path=parsed_args.config,schema_path = parsed_args.schema)
