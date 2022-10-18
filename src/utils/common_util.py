# insert sys path
import os
import datetime,time
from glob import glob


def get_latest_file(config,file_type):
    
    data_path = config['get_utility']['data_path']
    clean_data_path = config['get_utility']['clean_data_path']

    dates = {}
    try:
        if file_type == 'csv'.lower():
            files = glob(clean_data_path)
        else:
            files = glob(data_path)

        for name in files:
            dates.update({name:datetime.datetime.strptime(time.ctime(os.path.getmtime(name)), "%a %b %d %H:%M:%S %Y")})
    except:
        pass

    latest_file = max(dates,key = dates.get)

    return latest_file

def create_table_schema(Table_name,schema):
    last_col = list(schema.keys())[-1]
    query  = f'CREATE TABLE IF NOT EXISTS {Table_name} ('
    for column,d_type in schema.items():
        if column!=last_col:
            query+=f'{column} {d_type}, '

    query+=f'{last_col} {schema[last_col]} );'
    return query

# def insert_query(table_name,data,schema):
#     last_col = list(table_schema.keys())[-1]
#     col_str = ''
#     query = f'INSERT INTO {table_name}'
#     for col,value in schema.items():
#         if col!= last_col:
#             col_str+=f'{col}, '
#         else:
#             col_str+=f'{col} '
#             # ('+ '%s,' *(len(data.columns)-1)+ '%s' +f'),'
#     query+=f' ({col_str.strip()}) VALUES '
#     for ind,val in data.iterrows():
#         feed_data =tuple([str(val[col].date()) if col == 'Txn Date' else val[col] for col in data.columns[:]])
#         query+=f'{feed_data},'
#     return query[:-1]
