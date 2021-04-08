# standard libraries
import io
import os
import sys
import requests
import urllib
import json
from typing import Callable, Iterator, Optional, List
import collections

if sys.version_info >= (3, 6):
    from zipfile import ZipFile
else:
    from zipfile36 import ZipFile

# installed packages
import pandas as pd
from pandas import json_normalize
import xmltodict


# The master level function that handles reading XML string, file, and zipfile, as pandas dataframe.

def read_xml(path_or_xml: str, root_key_list: Optional[List[str]]=None, root_is_rows: bool=True, transpose: bool=False, encoding: Optional[str]=None) -> pd.DataFrame:
    if urllib.parse.urlparse(path_or_xml).scheme in ['http', 'https']:
        if path_or_xml.endswith('.zip'):
            with get_zip_file_from_url(path_or_xml) as zf:
                if len(get_files_list_in_zip(zf, '.xml')) > 0:
                    return read_xml_files_in_zip_as_dataframe(zf, root_key_list, root_is_rows=root_is_rows, transpose=transpose)
                elif len(get_files_list_in_zip(zf, '.zip')) > 0:
                    return read_xml_files_in_double_zip_as_dataframe(zf, root_key_list, root_is_rows=root_is_rows, transpose=transpose)
        elif path_or_xml.endswith('.xml'):
            return read_xml_as_dataframe(read_xml_from_url(path_or_xml), root_key_list, root_is_rows=root_is_rows, transpose=transpose)
        else:
            return read_xml_as_dataframe(read_xml_from_url(path_or_xml), root_key_list, root_is_rows=root_is_rows, transpose=transpose)
    else:
        if path_or_xml.endswith('.zip'):
            with get_zip_file_from_path(path_or_xml) as zf:
                if len(get_files_list_in_zip(zf, '.xml')) > 0:
                    return read_xml_files_in_zip_as_dataframe(zf, root_key_list, root_is_rows=root_is_rows, transpose=transpose)
                elif len(get_files_list_in_zip(zf, '.zip')) > 0:
                    return read_xml_files_in_double_zip_as_dataframe(zf, root_key_list, root_is_rows=root_is_rows, transpose=transpose)
        elif path_or_xml.endswith('.xml'):
            return read_xml_as_dataframe(read_xml_from_path(path_or_xml, encoding=encoding), root_key_list, root_is_rows=root_is_rows, transpose=transpose)
        else:
            return read_xml_as_dataframe(path_or_xml, root_key_list, root_is_rows=root_is_rows, transpose=transpose)


# These are very general functions to read xml data as dataframes

def get_to_root_in_dict(the_dict: dict, root_key_list: Optional[List[str]]=None) -> dict:
    if not root_key_list:
        return the_dict
    elif len(root_key_list) > 1:
        return get_to_root_in_dict(the_dict[root_key_list[0]], root_key_list[1:])
    else:
        return the_dict[root_key_list[0]]


def read_xml_as_dataframe(xml: str, root_key_list: Optional[List[str]]=None, root_is_rows: bool=True, transpose: bool=False) -> pd.DataFrame:
    if root_is_rows:
        return pd.DataFrame([get_to_root_in_dict(xmltodict.parse(xml), root_key_list)])
    elif transpose:
        return pd.DataFrame(get_to_root_in_dict(xmltodict.parse(xml), root_key_list)).T
    else:
        return pd.DataFrame(get_to_root_in_dict(xmltodict.parse(xml), root_key_list))


# These are helper functions to read xml files from url or within zip files

def get_zip_file_from_path(zip_path: str) -> ZipFile:
    return ZipFile(zip_path, 'r')

    
def get_zip_file_from_url(zip_url: str) -> ZipFile:
    return ZipFile(io.BytesIO(requests.get(zip_url).content))


def get_files_list_in_zip(zip_file: ZipFile, file_extension: str) -> List[str]:
    return [x for x in zip_file.namelist() if x.endswith(file_extension)]


def read_xml_from_path(path: str, encoding: Optional[str]=None) -> str:
    with open(path, 'r', encoding=encoding) as xf:
        return xf.read()


def read_xml_from_url(url: str) -> str:
    return requests.get(url).text


def read_xml_in_zip(zip_file: ZipFile, xml_file_name: str) -> str:
    with zip_file.open(xml_file_name) as xf:
        return xf.read()


def get_zip_in_zip(zip_file: ZipFile, zip_file_name: str) -> ZipFile:
    return ZipFile(io.BytesIO(zip_file.read(zip_file_name)))
    

def read_xml_files_in_zip_as_dataframe(zip_file: ZipFile, root_key_list: Optional[List[str]]=None, root_is_rows: bool=True, transpose: bool=False) -> pd.DataFrame:
    return pd.concat([read_xml_as_dataframe(read_xml_in_zip(zip_file, xml_file), root_key_list, root_is_rows=root_is_rows, transpose=transpose)
                      for xml_file in get_files_list_in_zip(zip_file, '.xml')],
                     sort=True, join='outer', ignore_index=True)


def read_xml_files_in_double_zip_as_dataframe(zip_file: ZipFile, root_key_list: Optional[List[str]]=None, root_is_rows: bool=True, transpose: bool=False) -> pd.DataFrame:
    return pd.concat([
        read_xml_files_in_zip_as_dataframe(
            get_zip_in_zip(zip_file, sub_zip_file),
            root_key_list,
            root_is_rows=root_is_rows,
            transpose=transpose)
        for sub_zip_file in get_files_list_in_zip(zip_file, '.zip')
    ])


# These are general functions to help deal with the tree-like structure (XML, JSON) that was read into the dataframe

def flatten(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        df = determine_flatten_action_for_column(df, column)(df, column)
    return df


def auto_flatten(df: pd.DataFrame, key_columns: List[str]=[]) -> pd.DataFrame:
    while action_recommended(df, key_columns):
        df = flatten(df)
    return df


def fully_flatten(df: pd.DataFrame, key_columns: List[str]=[]) -> pd.DataFrame:
    while action_required(df, key_columns):
        df = flatten(df)
    return df


def auto_separate_tables(df: pd.DataFrame, key_columns: List[str]) -> dict:
    data = {}
    main = df.pipe(auto_flatten, key_columns)
    main_table_name = list_separate_tables(main)[0].split('|')[0]

    for table in list_separate_tables(main):
        table_name = table.replace(main_table_name+'|', '', 1)
        table_columns = [
            column for column in main.columns
            if (column.startswith(table)) and (column not in key_columns)
        ]
        data[table_name] = (main[list(key_columns + table_columns)]
                            .dropna(axis='rows', how='all', subset=table_columns)
                            .pipe(fully_flatten, key_columns)
                            .drop_duplicates())
        data[table_name].columns = [column.replace(main_table_name+'|', '', 1) for column in data[table_name].columns]
        data[table_name].columns = [column.replace(table_name+'|', '', 1) for column in data[table_name].columns]
        main = (main[[column for column in main.columns
                      if column not in table_columns]])
    
    data[main_table_name] = main.drop_duplicates()
    data[main_table_name].columns = [column.replace(main_table_name+'|', '', 1) for column in data[main_table_name].columns]
    return data


# These are helper functions that enable the flattening and table separation.

def do_nothing(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return df


def explode(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return (df
            .explode(column)
            .reset_index(drop=True))

def normalise(df: pd.DataFrame, column: str) -> pd.DataFrame:
    return (df
            .reset_index(drop=True)
            .join(json_normalize(df[column], sep='|', max_level=0)
                  .add_prefix(str(column)+'|'))
            .drop(columns=[column])
            .rename(columns={f'{column}|#text': column}))


def mixed_explode(df: pd.DataFrame, column: str) -> pd.DataFrame:
    explodeable = df[column].apply(lambda x: type(x)==list)
    return pd.concat([df.loc[explodeable, :].pipe(explode, column), df.loc[~explodeable, :]]).reset_index(drop=True)


def mixed_normalise(df: pd.DataFrame, column: str) -> pd.DataFrame:
    normalisable = df[column].apply(lambda x: (type(x)==dict) | (type(x)==collections.OrderedDict))
    if df.loc[~normalisable, column].isna().all():
        return pd.concat([df.loc[normalisable, :].pipe(normalise, column),
                          df.loc[~normalisable, :]],
                         sort=True,
                         join='outer').pipe(lambda x: x.drop(columns=[column]) if x[column].isna().all() else x).reset_index(drop=True)
    else:
        return pd.concat([df.loc[normalisable, :].pipe(normalise, column),
                          df.loc[~normalisable, :]],
                         sort=True,
                         join='outer').reset_index(drop=True)


def determine_flatten_action_for_column(df: pd.DataFrame, column: str) -> Callable:
    column_data_types = df[column].apply(lambda x: type(x))
    if (column_data_types == list).all(skipna=True):
        return explode
    elif (column_data_types == dict).all(skipna=True) or (column_data_types == collections.OrderedDict).all(skipna=True):
        return normalise
    elif (column_data_types == list).any():
        return mixed_explode
    elif (column_data_types == dict).any() or (column_data_types == collections.OrderedDict).any():
        return mixed_normalise
    else:
        return do_nothing


def action_required(df: pd.DataFrame, key_columns: List[str]=[]) -> bool:
    return any(determine_flatten_action_for_column(df, column) != do_nothing
               for column in df.columns if column not in key_columns)


def action_recommended(df: pd.DataFrame, key_columns: List[str]=[]) -> bool:
    return all(determine_flatten_action_for_column(df, column) != do_nothing
               for column in df.columns if column not in key_columns)


def list_separate_tables(df: pd.DataFrame) -> list:
    potential_separate_table = list(set([
        '|'.join(column.split('|')[:-1])
        for column in df.columns
        if determine_flatten_action_for_column(df, column).__name__ != "do_nothing"
    ]))
    potential_separate_table.sort()

    separate_tables_list = potential_separate_table
    for i, potential in enumerate(potential_separate_table):
        if (i < len(potential_separate_table) - 1) and (potential_separate_table[i+1].startswith(potential)):
            separate_tables_list.remove(potential_separate_table[i+1])
    if separate_tables_list == ['']:
        return ['main']+potential_separate_table
    else:
        return [column for column in df.columns
                if determine_flatten_action_for_column(df, column).__name__ != "do_nothing"]
