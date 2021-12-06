import hashlib
import math
from numpy import NaN, nan
import pandas as pd
import random
import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import plotly.graph_objects as go
# random.seed(0)

from static_abilities import StaticAbilities

# TODO: card name, artwork, mana/money cost, special abilities


def generate_encoding():
    # Card ability encodings
    df = pd.DataFrame(columns=['Hex', 'Ability'])
    ids = [x for x in range(256)]
    hexs = [hex(x) for x in ids]
    df['Hex'] = hexs
    df['Ability'] = pd.Series([e.name for e in StaticAbilities])

    return df


def generate_hashes(nb_cards=100, sha_input_scale_factor=1000):

    # Creating sha-256 hashes
    random_inputs = [random.random() * x for x in [sha_input_scale_factor] * nb_cards]
    strings = [str(x) for x in random_inputs]
    encoded = [s.encode() for s in strings]
    hashes = [hashlib.sha256(s).hexdigest() for s in encoded]

    return hashes


def build_cards(hashes):
    # Returns dataframe with hash to encodings comparison

    # Checking the hash for matching encodings
    nb_abilities_list = []
    abilities_list = []
    power_list = []
    toughness_list = []
    price_list = []

    for hash in hashes:
        byte_array = bytearray.fromhex(hash)
        
        nb_abilities = 0
        abilities = []
        power = 0
        thoughness = 0
        price = 0

        for i, byte in enumerate(byte_array):
            # Power, toughness and price bytes may appear anywhere in hash
            price += sum(df_encoding.index[:32] == byte)
            thoughness += sum(df_encoding.index[33:48] == byte)
            power += sum(df_encoding.index[49:64] == byte)
            nb_abilities += sum(df_encoding.index[:nb_encoded_abilites] == byte)
            ab = df_encoding.iloc[int(byte)]['Ability']
            if isinstance(ab, str):
                abilities.append(ab)

            # Ability bytes must appear at correct position to be valid
            # if df_encoding.index[i] == byte:
            #     abilities += 1
        
        nb_abilities_list.append(nb_abilities)
        abilities_list.append(abilities)
        power_list.append(power)
        toughness_list.append(thoughness)
        price_list.append(price)

    df_cards = pd.DataFrame({'Price': price_list,
                            'Power': power_list, 
                            'Toughness': toughness_list, 
                            '# Abilities': nb_abilities_list,
                            'Abilities': abilities_list,
                            'Hash': hashes})

    return df_cards


def drop_nonvalid_cards(df_cards, drop_cons):
    # Dropping useless and overpowered cards
    for con in drop_cons.keys():
        ids = df_cards[drop_cons[con]].index
        print('Dropping cards with {}: {}'.format(con, len(ids)))
        df_cards = df_cards.drop(ids)

    return df_cards


def plot_attribute_distribution(df_cards):

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

    fig = plotly.subplots.make_subplots(rows=1, cols=4,
                                        subplot_titles=df_cards.columns[:4])
    fig.update_layout(title_text=f'Attribute distributions of {len(df_cards)} cards', yaxis_title='# Cards')

    for i in range(4):
        bars = df_cards.iloc[:, i].value_counts(normalize=True)
        fig.append_trace(
            go.Bar(x=bars.index, y=bars.values, name=df_cards.columns[i], marker_color=colors[i]),
            row=1, col=i+1
        )

    fig.show()


if __name__ == '__main__':

    plot = True
    nb_cards = 1000
    
    # 17 as of now
    nb_encoded_abilites = len(StaticAbilities)

    df_encoding = generate_encoding()
    hashes = generate_hashes(nb_cards)
    df_cards = build_cards(hashes)

    # Conditions that make a card non-valid (overpowered/unplayable/whack-ass weak)
    drop_conditions = {'no toughness': df_cards['Toughness'] == 0, 
                'insane powers': (df_cards['Toughness'] > 3) & (df_cards['Power'] > 3) & (df_cards['Price'] < 2),
                'too many abilities': df_cards['# Abilities'] > 4}

    df_cards = drop_nonvalid_cards(df_cards, drop_conditions)

    print('Remaining cards: {}'.format(df_cards.shape[0]))
    print(df_cards)
    df_cards.to_csv('cards.csv')

    if plot:
        plot_attribute_distribution(df_cards)   

    exit()
