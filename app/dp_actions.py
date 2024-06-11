# Data Preparation Actions

import pandas as pd
import re
import streamlit as st

def list_actions():
    return [
        "Remove column",
        "Split column",
        "Remove rows with empty values",
        "Fill empty values with zeroes",
        "Fill empty values with the median of a group column",
        "Format dates",
        "Format phone numbers",
    ]

def add_action_parameters(action, columns):
    match action:
        case "Split column": return {
            "delimiter": st.text_input('Delimiter', value=','),
            "split_limit": st.number_input('Split limit', 0, help='A limit of zero will split all occurrences')
        }
        case "Fill empty values with the median of a group column": return {
            "group_column": st.selectbox("Group Column", columns)
        }
        case "Format dates": return {
            "date_format": st.radio("Date Format", ['YYYY-MM-DD', 'DD/MM/YYYY', 'MM/DD/YYYY'])
        }
        case "Format phone numbers": return {
            "phone_format": st.radio("Phone Format", ['Add Separators ( (xx)xxxxx-xxxx )', 'Remove Separators ( xxxxxxxxxxx )'])
        }

def remove_column(df: pd.DataFrame, column: str):
    return df.drop(column)

def split_column(df: pd.DataFrame, column: str, delimiter: str, split_limit: int):
    new_cols = df[column].str.split(delimiter, expand=True, n=split_limit)
    new_col_names = [f'{column}_{i+1}' for i in range(new_cols.shape[1])]
    df[new_col_names] = new_cols
    return df

# def remove_duplicate_rows(df: pd.DataFrame):
#     return df.drop_duplicates()

def remove_empty_rows(df: pd.DataFrame, column: str):
    return df.dropna(subset=[column])

def fill_empty_values_with_zeroes(df: pd.DataFrame, column: str):
    df_num = df[column].fillna(0)
    return pd.concat([df_num, df.drop(column)], axis=1)

def fill_empty_values_with_median(df: pd.DataFrame, column: str, group_column: str):
    groups = df[group_column].to_list()
    medians = df.dropna(subset=[column]).groupby(group_column)[column].median()
    for groups, median in medians.items():
        df.loc[(df[group_column] == groups) & (df[column].isnull()), column] = median
    return [df, medians]

def format_dates(df: pd.DataFrame, column: str, date_format: str):
    def apply_function(date_str):
        try:
            match date_format:
                case 'YYYY-MM-DD': format = '%Y-%m-%d'
                case 'DD/MM/YYYY': format = '%d/%m/%Y'
                case 'MM/DD/YYYY': format = '%m/%d/%Y'
            return pd.to_datetime(date_str, errors='raise').strftime(format) if str(date_str) else None
        except ValueError:
            return date_str
    return df[column].apply(apply_function)

def format_phone_number(df: pd.DataFrame, column: str, phone_format: str):
    def apply_function(phone):
        phone_digits = re.sub(r'\D', '', str(phone))    
        if phone_format == 'Add Separators ( (xx)xxxxx-xxxx )':
            if len(phone_digits) == 11:
                return re.sub(r'(\d{2})(\d{5})(\d{4})', r'(\1) \2-\3', phone_digits)
            elif len(phone_digits) == 10:
                return re.sub(r'(\d{2})(\d{4})(\d{4})', r'(\1) \2-\3', phone_digits)
            else:
                return phone
        else:
            return phone_digits if str(phone_digits) else None
    return df[column].apply(apply_function)
