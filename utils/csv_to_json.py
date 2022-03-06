import pandas as pd
import json
import os


def fit_json(df):

    df.drop(labels=['Unnamed: 0', '# Keyword Abilities', '# Special Abilities', '# Triggers'], axis=1, inplace=True)
    df.rename(columns={"Name": "title",  
                       "Price": "cost",
                       "Power": "attack",
                       "Toughness": "health",
                       "Keyword Abilities": "keyword_abilities",
                       "Special Abilities": "special_abilities",
                       "Triggers": "triggers",
                       "Hash": "hash"}, inplace=True)
    
    return df


def main():

    # find .csv files in current directory
    csv_files = [f for f in os.listdir(PATH) if f.endswith('.csv')]

    # read csv files
    for csv_file in csv_files:
        df = pd.read_csv(csv_file)
        df = fit_json(df)
        df.to_json(orient="table", index=False, path_or_buf=csv_file.replace('.csv', '.json'))
        
    return

if __name__ == "__main__":
    PATH = r'C:\Users\m-wue\Desktop\Sors\NFT-game'

    main()
    