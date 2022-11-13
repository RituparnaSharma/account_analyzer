import os
import psycopg2
from utils.common_util import create_table_schema
from dotenv import load_dotenv
load_dotenv()

# connect to postgress
def connect():
    try:

        conn = psycopg2.connect(database = os.getenv('pg_database'), user = os.getenv('pg_user'), password = os.getenv('pg_password'), host = os.getenv('pg_host'), port = os.getenv('pg_port'))
        cur = conn.cursor()
        print("Successfully connected to database")
    except psycopg2.Error as e:
        print("Error: couldnot make connection to postgres database")
        print(e)

    conn.set_session(autocommit = True)

    return conn,cur

# create postgres table 
def create_table(get_name,schema,cur):
    try:
        # data_dic = get_table_info(pg_acc_data)
        for table_name in  get_name:
            cur.execute(f"{create_table_schema(table_name,schema)}")
            print(f'Table {table_name} sucessfully created')
        
    except psycopg2.Error as e:
        print("Error: cannot create table")
        print(e)

# insert table values
def insert_table(csv_path,table_name,cur):
    try:
        query  = f'''copy {table_name} from '{csv_path}' delimiter ','  csv; '''
        cur.execute(query)
        print(f'Data inserted for table {table_name} succefully')
    except psycopg2.Error as e:
        print(f"Error: can not insert values for table {table_name}")
        print(e)

