import hashlib
import math
from numpy import NaN, nan
import pandas as pd
import random
import matplotlib.pyplot as plt
import plotly
import plotly.express as px
import plotly.graph_objects as go
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from Encodings.keyword_abilities import KeywordAbilities
from Encodings.special_abilities import SpecialAbilities
from Encodings.ability_triggers import AbilityTriggers

from Artworks.generate_artwork import draw_artwork

# TODO: card name, artwork, mana/money cost, special abilities


def generate_encodings():
    # Card ability encodings
    df = pd.DataFrame(columns=['Hex', 'Ability'])
    ids = [x for x in range(256)]
    hexs = [hex(x) for x in ids]
    df['Hex'] = hexs
    df['Keyword Ability'] = pd.Series([e.name for e in KeywordAbilities])
    # Shifting by NB_KW_ABILITIES to not have same byte encoding produce same abilities
    df['Special Ability'] = pd.Series([e.name for e in SpecialAbilities])
    df['Special Ability'] = df['Special Ability'].shift(NB_KW_ABILITIES)
    # Shifting again
    df['Ability Trigger'] = pd.Series([e.name for e in AbilityTriggers])
    df['Ability Trigger'] = df['Ability Trigger'].shift(NB_KW_ABILITIES + NB_SP_ABILITIES)


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

    # Int for card
    price_list = []         # in [0; price_enc]
    power_list = []         # in [0; thg_enc]
    toughness_list = []     # in [0; pow_enc]

    # Lists with number of abilities/triggers for easier data handling 
    nb_kw_ab_list = []
    nb_sp_ab_list = []
    nb_trig_list = []
    # Lists with the abilities/triggers as defined in df_encodings
    kw_ab_list = []
    sp_ab_list = []
    trig_list = []

    print('Generating cards...')
    for hash in tqdm(hashes):
        byte_array = bytearray.fromhex(hash)
        
        power = 0
        thoughness = 0
        price = 0
        kw_abilities = []
        sp_abilities = []
        triggers = []

        for i, byte in enumerate(byte_array):
            # Power, toughness and price bytes may appear anywhere in hash
            price += sum(df_encoding.index[:NB_PRICE_ENC] == byte)
            thoughness += sum(df_encoding.index[NB_PRICE_ENC+1:NB_PRICE_ENC+NB_THG_ENC] == byte)
            power += sum(df_encoding.index[NB_PRICE_ENC+NB_THG_ENC+1:NB_PRICE_ENC+NB_THG_ENC+NB_POW_ENC] == byte)

            # Card abilites
            kw_ab = df_encoding.iloc[int(byte)]['Keyword Ability']
            if isinstance(kw_ab, str):
                if not kw_ab in kw_abilities:
                    kw_abilities.append(kw_ab)

            sp_ab = df_encoding.iloc[int(byte)]['Special Ability']
            if isinstance(sp_ab, str):
                if not sp_ab in sp_abilities:
                    sp_abilities.append(sp_ab)
            
            trig = df_encoding.iloc[int(byte)]['Ability Trigger']
            if isinstance(trig, str):
                if not trig in triggers:
                    triggers.append(trig)

            # Ability bytes must appear at correct position to be valid
            # if df_encoding.index[i] == byte:
            #     abilities += 1

        price_list.append(price)
        power_list.append(power)
        toughness_list.append(thoughness)

        nb_kw_ab_list.append(len(kw_abilities))
        kw_ab_list.append(kw_abilities)
        nb_sp_ab_list.append(len(sp_abilities))
        sp_ab_list.append(sp_abilities)
        nb_trig_list.append(len(triggers))
        trig_list.append(triggers)

    df_cards = pd.DataFrame({'Price': price_list,
                            'Power': power_list, 
                            'Toughness': toughness_list, 
                            '# Keyword Abilities': nb_kw_ab_list,
                            '# Special Abilities': nb_sp_ab_list,
                            '# Triggers': nb_trig_list,
                            'Keyword Abilities': kw_ab_list,
                            'Special Abilities': sp_ab_list,
                            'Triggers': trig_list, 
                            'Hash': hashes})

    return df_cards


def drop_nonvalid_cards(df_cards, drop_cons, drop_trig_without_ab=True):
    # Dropping useless and overpowered cards
    for con in drop_cons.keys():
        ids = df_cards[drop_cons[con]].index
        print('Dropping cards with {}: {}'.format(con, len(ids)))
        df_cards = df_cards.drop(ids)

    # Dropping Triggers for no corresponding special ability
    if drop_trig_without_ab:
        ids = []
        for id, card in df_cards.iterrows():
            if card['# Triggers'] > card['# Special Abilities']:
                ids.append(id)
        print('Dropping cards with more triggers than abilities: {}'.format(len(ids)))
        df_cards = df_cards.drop(ids)

    return df_cards


def plot_attribute_distribution(df_cards, nb_cards, subplots=False):

    colors = px.colors.qualitative.Set1

    if subplots:
        nb_rows, nb_cols = 2, 3
        fig = plotly.subplots.make_subplots(rows=nb_rows, cols=nb_cols,
                                            subplot_titles=df_cards.columns[:6],
                                            y_title='# Cards')
        row = 1
        for i in range(6):
            if i == nb_cols:
                row = 2
            bars = df_cards.iloc[:, i].value_counts(normalize=False)
            fig.append_trace(
                go.Bar(x=bars.index, y=bars.values, name=df_cards.columns[i], marker_color=colors[i]),
                row=row, col=(i%nb_cols)+1
            )

    else:
        data = []
        for i in range(6):
            bars = df_cards.iloc[:, i].value_counts()
            data.append(go.Bar(x=bars.index, y=bars.values,
                        name=df_cards.columns[i],
                        marker_color=colors[i])
                        )

        fig = go.Figure(data=data)
        fig.update_layout(barmode='group')

    fig.update_layout(title_text=f'Attribute distributions of {len(df_cards)} cards (from originally {nb_cards})', 
                      template='plotly_dark')
    fig.show()


if __name__ == '__main__':

    plot = False
    draw = True
    nb_cards = 50

    # random.seed(0)

    # MAX_ENCODING = int('0b11111111', 2)
    NB_KW_ABILITIES = len(KeywordAbilities)
    NB_SP_ABILITIES = len(SpecialAbilities)

    # The higher nb encodings, the more likely byte matches are
    NB_PRICE_ENC = 32
    NB_THG_ENC = 16
    NB_POW_ENC = 16

    df_encoding = generate_encodings()
    hashes = generate_hashes(nb_cards)
    df_cards = build_cards(hashes)

    # Conditions that make a card non-valid (overpowered/unplayable/whack-ass weak)
    drop_conditions = {'no toughness': df_cards['Toughness'] == 0, 
                'insane powers': (df_cards['Toughness'] > 3) & (df_cards['Power'] > 3) & (df_cards['Price'] < 2),
                'too many abilities': df_cards['# Keyword Abilities'] > 4}
                #'Trigger without ability': len(df_cards['Triggers']) > len(df_cards['Special Abilities'])}
    df_cards = drop_nonvalid_cards(df_cards, drop_conditions)

    print('Remaining cards: {}'.format(df_cards.shape[0]))
    # print(df_cards.drop(labels=['# Keyword Abilities', '# Special Abilities', '# Triggers'], axis=1))
    df_cards.to_csv('cards.csv')

    if plot:
        plot_attribute_distribution(df_cards, nb_cards)

    if draw:  

        cards = df_cards.drop(labels=['Keyword Abilities', 'Special Abilities', 'Triggers'], axis=1)
        print('Generating artworks...')
        for id, card in tqdm(cards.iterrows()):
            draw_artwork(card)
        
    exit()
