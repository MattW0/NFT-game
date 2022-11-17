import pandas as pd
import json
import os


def format_df_for_json(df):

    #df.drop(labels=['Unnamed: 0', '# Keyword Abilities', '# Special Abilities', '# Triggers'], axis=1, inplace=True)
    df.drop(labels=['# Keyword Abilities', '# Special Abilities', '# Triggers'], axis=1, inplace=True)
    
    df.rename(columns={"Name": "title",  
                       "Price": "cost",
                       "Power": "attack",
                       "Toughness": "health",
                       "Keyword Abilities": "keyword_abilities",
                       "Special Abilities": "special_abilities",
                       "Triggers": "triggers",
                       "Hash": "hash"}, inplace=True)
    
    return df


def save_json(df):
    
    df = format_df_for_json(df)
    df.to_json(orient="records", path_or_buf='cards.json')
        
    return