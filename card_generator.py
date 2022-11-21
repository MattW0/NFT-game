import hashlib
import math
from numpy import NaN, nan
import pandas as pd
import random
import plotly
import plotly.express as px
import plotly.graph_objects as go
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from Encodings.keyword_abilities import KeywordAbilities
from Encodings.special_abilities import SpecialAbilities
from Encodings.ability_triggers import AbilityTriggers

from utils.generate_artwork import draw_artwork
from utils.csv_to_json import save_json

# TODO: card name, artwork, mana/money cost, special abilities


def generate_encodings():
    # Card ability encodings
    ids = [x for x in range(256)]
    hexs = [hex(x) for x in ids]
    df = pd.DataFrame({'Hex': hexs})

    shift_static = NB_THG_ENC + NB_POW_ENC + NB_POINTS_ENC

    # Shifting by some amount each time to not have same byte encoding result in better stats
    df['Keyword Ability'] = pd.Series([e.name for e in KeywordAbilities])
    df['Keyword Ability'] = df['Keyword Ability'].shift(shift_static)

    df['Special Ability'] = pd.Series([e.name for e in SpecialAbilities])
    df['Special Ability'] = df['Special Ability'].shift(shift_static + NB_KW_ABILITIES)

    df['Ability Trigger'] = pd.Series([e.name for e in AbilityTriggers])
    df['Ability Trigger'] = df['Ability Trigger'].shift(shift_static + NB_KW_ABILITIES + NB_SP_ABILITIES)

    df.to_csv('Encodings/encodings.csv', index=False)

    return df


def generate_cardnames():

    if nb_cards == 1:
        name = input("Please enter a card name: ")
        return [name.strip()]

    # read names.txt to have titles and inputs for cards
    names = []
    with open(namesFile, 'r') as f:
        for line in f:
            names.append(line.strip())

    random.shuffle(names)

    return names[:nb_cards]


def generate_hashes(nb_cards=100, names=None, sha_input_scale_factor=1000):

    # Random numbers converted to strings
    if names is None:
        random_inputs = [random.random() * x for x in [sha_input_scale_factor] * nb_cards]
        names = [str(x) for x in random_inputs]

    encoded = [s.encode() for s in names[:nb_cards]]
    hashes = [hashlib.sha256(s).hexdigest() for s in encoded]

    return hashes


def build_cards(hashes, names, df_encoding):
    # Returns dataframe with hash to encodings comparison

    # Int for card
    toughnesses = []    
    powers = []         
    points = []         

    # Lists with number of abilities/triggers for easier data handling (used in draw artwork)
    nb_kw_ab = []
    nb_sp_ab = []
    nb_trig = []
    # Lists with the abilities/triggers as defined in df_encodings
    keyword_abilities = []
    special_abilities = []
    triggers = []

    print('Generating cards...')
    for hash in tqdm(hashes):
        print(hash)
        byte_array = bytearray.fromhex(hash)
        
        card_power = 0
        card_thoughness = 1
        card_points = 0

        card_kw_abilities = []
        card_sp_abilities = []
        card_triggers = []

        for index, byte in enumerate(byte_array):
            # Power, toughness increase when matched with one up to NB__ENC encoding bytes
            card_thoughness += sum(df_encoding.index[:NB_THG_ENC] == byte)
            card_power += sum(df_encoding.index[NB_THG_ENC+1:NB_THG_ENC+NB_POW_ENC] == byte)
            card_points += sum(df_encoding.index[NB_POW_ENC+NB_THG_ENC+1 : NB_POW_ENC+NB_THG_ENC+NB_POINTS_ENC] == byte)

            # Specific card abilites are added when the byte matches the exact encoding
            if index in KW_BYTES_RANGE:
                kw_ab = df_encoding.iloc[int(byte)]['Keyword Ability']
                if isinstance(kw_ab, str):
                    if not kw_ab in card_kw_abilities:
                        card_kw_abilities.append(kw_ab)

            if index in SP_BYTES_RANGE:
                sp_ab = df_encoding.iloc[int(byte)]['Special Ability']
                if isinstance(sp_ab, str):
                    if not sp_ab in card_sp_abilities:
                        card_sp_abilities.append(sp_ab)
            
            if index in TR_BYTES_RANGE:
                trig = df_encoding.iloc[int(byte)]['Ability Trigger']
                if isinstance(trig, str):
                    if not trig in card_triggers:
                        card_triggers.append(trig)
                    
        powers.append(card_power)
        toughnesses.append(card_thoughness)
        points.append(card_points)

        keyword_abilities.append(card_kw_abilities)
        special_abilities.append(card_sp_abilities)
        triggers.append(card_triggers)
        
        nb_kw_ab.append(len(card_kw_abilities))
        nb_sp_ab.append(len(card_sp_abilities))
        nb_trig.append(len(card_triggers))

    df_cards = pd.DataFrame({'Name': names,
                            'Power': powers, 
                            'Toughness': toughnesses,
                            'Points': points,
                            '# Keyword Abilities': nb_kw_ab,
                            '# Special Abilities': nb_sp_ab,
                            '# Triggers': nb_trig,
                            'Keyword Abilities': keyword_abilities,
                            'Special Abilities': special_abilities,
                            'Triggers': triggers, 
                            'Hash': hashes})

    return df_cards


def balance_cards(df_cards, drop_trig_without_ab=True):
    
    # I dont want to drop cards because result needs to be "random" but deterministic
    # Each card name must result in a valid card!
    # rather balance overpowered cards by reducing nb abilities or increasing price
    # right now cards are too expensive with too many triggers and abilities 
    # -> TODO: balance cards by stronger restrictions on abilities and triggers or dropping in some deterministic way
    
    drop_cons = {
        # 'insane powers': (df_cards['Toughness'] > 3) & (df_cards['Power'] > 3) & (df_cards['Price'] < 2),
        # 'too many abilities': df_cards['# Keyword Abilities'] > 4
    }
        
    # Dropping useless and overpowered cards
    for con in drop_cons.keys():
        ids = df_cards[drop_cons[con]].index
        print('Dropping cards with {}: {}'.format(con, len(ids)))
        df_cards = df_cards.drop(ids)

    # Dropping Triggers for no corresponding special ability
    # if drop_trig_without_ab:
    #     ids = []
    #     for id, card in df_cards.iterrows():
    #         if card['# Triggers'] > card['# Special Abilities']:
    #             ids.append(id)
    #     print('Dropping cards with more triggers than abilities: {}'.format(len(ids)))
    #     df_cards = df_cards.drop(ids)

    return df_cards


def relate_triggers_and_special_abilities(df_cards):
    # Relates triggers to special abilities
    
    texts = []
    for card in df_cards.iterrows():

        text = []
        name = card[1]['Name']
        triggers = card[1]['Triggers']
        special_abilities = card[1]['Special Abilities']

        nbTriggers = len(triggers)
        nbSpecialAbilities = len(special_abilities)

        if nbTriggers == 0 or nbSpecialAbilities == 0:
            texts.append(text)
            continue

        for trig in triggers:
            text.append(f'Whenever {name} {trig} ' + special_abilities[random.randint(0, nbSpecialAbilities-1)])

        texts.append(text)

    df_cards["Triggers text"] = texts

    return df_cards


def price_cards(df_cards):
    # TODO: Find function to make price have low mean, large variance and skewed to left (lots of cheaper cards and few expensive)

    prices = []
    for card in df_cards.iterrows():
        # Name, Power, Toughness, # Keyword Abilities, # Special Abilities, # Triggers
        _, pow, thg, pts, kw, sp, tr, _, _, _, _ = card[1]

        price = math.floor((thg + pow)/3 + (kw + sp + tr)*0.5 + pts)
        prices.append(price)

    df_cards.insert(loc=1, column='Price', value=prices)

    return df_cards


def plot_attribute_distribution(df_cards, nb_cards, subplots=False):

    colors = px.colors.qualitative.Set1

    if subplots:
        nb_rows, nb_cols = 2, 3
        fig = plotly.subplots.make_subplots(rows=nb_rows, cols=nb_cols,
                                            subplot_titles=df_cards.columns[:6],
                                            y_title='# Cards')
        row = 1
        for i in range(NB_ATTRIBUTES):
            if i == nb_cols:
                row = 2
            bars = df_cards.iloc[:, i].value_counts(normalize=False)
            fig.append_trace(
                go.Bar(x=bars.index, y=bars.values, name=df_cards.columns[i], marker_color=colors[i]),
                row=row, col=(i%nb_cols)+1
            )

    else:
        data = []
        for i in range(1, NB_ATTRIBUTES+1):
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


def main():

    # read names.txt to have titles and inputs for cards
    names = generate_cardnames()
    df_encoding = generate_encodings()
    hashes = generate_hashes(nb_cards, names)
    
    df_cards = build_cards(hashes, names, df_encoding)
    df_cards = balance_cards(df_cards)
    df_cards = price_cards(df_cards)
    df_cards = relate_triggers_and_special_abilities(df_cards)
    print(df_cards.head(8))
    
    if plot and nb_cards > 1:
        plot_attribute_distribution(df_cards, nb_cards)

    if make_artwork:  
        cards = df_cards.drop(labels=['Keyword Abilities', 'Special Abilities', 'Triggers'], axis=1)
        print('Generating artworks...')
        for _, card in tqdm(cards.iterrows()):
            draw_artwork(card)

    print('Remaining cards: {}'.format(df_cards.shape[0]))
    save_json(df_cards)

    df_cards.to_csv('cards.csv', index=False)
    
    return


if __name__ == '__main__':

    namesFile = r'.\Names\first_names.txt'
    plot = True
    nb_cards = 1
    make_artwork = False

    random.seed(0)

    NB_ATTRIBUTES = 7 # Price, Power, Toughness, Points, Keyword Abilities, Special Abilities, Triggers
    NB_KW_ABILITIES = len(KeywordAbilities)
    NB_SP_ABILITIES = len(SpecialAbilities)

    # A larger range corresponds to more byte matches and thus more abilities
    KW_BYTES_RANGE = range(0, 15)
    SP_BYTES_RANGE = range(16, 23)
    TR_BYTES_RANGE = range(24, 31)

    # The higher nb encodings, the more likely byte matches are
    NB_THG_ENC = 24
    NB_POW_ENC = 24
    NB_POINTS_ENC = 8

    
    main()
