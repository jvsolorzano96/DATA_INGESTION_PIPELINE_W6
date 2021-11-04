import logging
import os
import subprocess
import yaml
import pandas as pd
import datetime 
import gc
import re
import dask.dataframe as dd 
#This file contains all the functions needed to validate our data ingestion
def load_config_file(config_name,config_path):
    '''
    Function to load YAML config file
    '''
    with open(os.path.join(config_path,config_name)) as file:
        config = yaml.safe_load(file)
    return config

def load_data(config_name):
    data = dd.read_csv(os.path.join(config_name['data_directory'], config_name['data_name']),low_memory=False)
    print('Data Uploaded from',config_name['data_directory'],' name = ',config_name['data_name'])
    return data

def drop_irrelevant(data, config_name):
    data = data.drop(config_name['drop_columns'],axis=1)
    return data

def replacer(string, char):
    pattern = char + '{2,}'
    string = re.sub(pattern, char, string) 
    return string



def headers_validation(data,config_name):
    '''
    This function performs replacements on whitespaces and
    standarized the column names 
    '''
    if len(data.columns) == len(config_name['columns_names']):
        data.columns = config_name['columns_names']
        data.columns = data.columns.str.lower() #Converts column names into lowercase 
        data.columns = data.columns.str.replace('[^\w]','_',regex=True) #Replace Regex and whitesapces with '_'
        data.columns = list(map(lambda x: x.strip('_'), list(data.columns)))#Remove the last strip '_'
        data.columns = list(map(lambda x: replacer(x,'_'), list(data.columns)))#Remove doble under score'__'
        expected_col = list(map(lambda x: x.lower(), config_name['columns_names']))
        expected_col.sort()
        data.columns =list(map(lambda x: x.lower(), list(data.columns)))
        #data = data.reindex(sorted(data.columns), axis=1)
        if len(data.columns) == len(expected_col):
            print("Columns headers validation passed")
            return 1
        else:
            print("column name and column length validation failed")
            mismatched_columns_file = list(set(data.columns).difference(expected_col))
            print("Following File columns are not in the YAML file",mismatched_columns_file)
            missing_YAML_file = list(set(expected_col).difference(data.columns))
            print("Following YAML columns are not in the file uploaded",missing_YAML_file)
            logging.info(f'DataFrame columns: {data.columns}')
            logging.info(f'expected columns: {expected_col}')
            return 0
    else:
        print("Columns length validation failed")
        len(data.columns)
        print("You have ",len(data.columns),' colummns, you are supposed to read ',len(config_name['columns_names']), 'columns')
    
def rename_columns (data,config_name):
	data.columns= config_name["columns_names"]
	return data.head(2)
        
def memory_usage_optimization(data,config_name):
    data['client_id'] = data['client_id'].astype(config_name['data_type']['client_id'])
    data['age_start_observed'] = data['age_start_observed'].astype(config_name['data_type']['age_start_observed'])
    data['age_end'] = data['age_end'].astype(config_name['data_type']['age_end'])
    data['is_truncated'] = data['is_truncated'].astype(config_name['data_type']['is_truncated'])
    data['is_censored'] = data['is_censored'].astype(config_name['data_type']['is_censored'])
    data['is_dead'] = data['is_dead'].astype(config_name['data_type']['is_dead'])
    return data
			

def drop_missing_values(data):
    data= data.dropna()
    return data

def save_clean_data(data,config_name):
    data.to_parquet(os.path.join(config_name['data_clean_folder'],config_name['clean_data']), compression='gzip')        
    return('Data saved as ',config_name['clean_data'])
    
