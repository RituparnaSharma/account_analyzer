import os
import re
import argparse
import pandas as pd
from datetime import datetime
from get_data import read_params,get_data

def load_and_preprocess(config_path):
    config = read_params(config_path)
    contents = get_data(config_path)

    # get destination path
    curr_dt = datetime.now().strftime('%y%m%d%H%M%S')
    dest_data_path = os.path.join(config['destination']['clean_data_source_csv'],f'sbi{curr_dt}.csv')

    # Variables
    commaDelList = []
    rowList = []
    foundData = False

    for row in contents:
        if "Txn Date" in row:
            foundData = True
        if foundData:
            rowList.append(row)

    for row in rowList:
        if row != rowList[-1]:
            commaDelList.append(row.split("\t"))

    # create dataframe
    df = pd.DataFrame(commaDelList).reset_index(drop=True)

    # Data cleaning
    df = df[1:-1]
    if len(df.columns)==8:
        df.drop(df.columns[-1],axis=1,inplace=True)
    df.columns = ['Txn_Date','Value_Date','Description','Ref_cheque_No','Debit' ,'Credit','Balance']
    df['Debit'] = df['Debit'].apply(lambda row : re.sub(r'"','',row.split('\n')[0]))
    df['Credit'] = df['Credit'].apply(lambda row : re.sub(r'"','',row.split('\n')[0]))
    df['Balance'] = df['Balance'].apply(lambda row : re.sub(r'"','',row.split('\n')[0]))

    # # store as csv
    df.to_csv(dest_data_path,index=False)


if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--config",default = "../params.yml")
    parsed_args = args.parse_args()
    data = load_and_preprocess(config_path=parsed_args.config)
