import hashlib
import math
# from numpy import NaN, nan
import pandas as pd
import random
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

from Encodings.keyword_abilities import KeywordAbilities
from Encodings.special_abilities import SpecialAbilities
from Encodings.ability_triggers import AbilityTriggers

from utils.card_finalize import evaluate_keywords, relate_triggers_and_special_abilities, balance_cards
from utils.plotting import plot_attribute_distribution
from utils.generate_artwork import draw_artwork
from utils.csv_to_json import save_json


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


def price_cards(df_cards):
    # TODO: Find function to make price have low mean, large variance and skewed to left (lots of cheaper cards and few expensive)
    # TODO: Consider type of relations (exiling >> destroying, ...)
    # TODO: Maybe with additional costs after creation (eg. "You may sac a creature, if you did exile target creature")
    #    Or You may pay 5 cash, if you did, take control of target creature

    prices = []
    for card in df_cards.iterrows():
        # _, Power, Toughness, points, # Keyword Abilities, # Special Abilities, # Triggers, _, _, _, _, _, # Relations
        _, pow, thg, pts, kw, sp, tr, _, _, _, _, _, nb_rel = card[1]

        price = math.floor((thg + pow)/3 + kw*0.5 + nb_rel + pts)
        prices.append(price)

    df_cards.insert(loc=1, column='Price', value=prices)

    return df_cards


def main():

    # read names.txt to have titles and inputs for cards
    names = generate_cardnames()
    df_encoding = generate_encodings()
    hashes = generate_hashes(nb_cards, names)
    
    df_cards = build_cards(hashes, names, df_encoding)
    df_cards = balance_cards(df_cards)
    df_cards = relate_triggers_and_special_abilities(df_cards)
    df_cards = evaluate_keywords(df_cards)
    df_cards = price_cards(df_cards)
    print(df_cards.head(8))

    if plot and nb_cards > 1:
        plot_attribute_distribution(df_cards, ATTRIBUTES_TO_PLOT)
    
    # sort by number of Triggers Text
    df_cards = df_cards.sort_values(by=['# Relations'], ascending=False)

    # save to csv (for easy inspection) and json (for Unity)
    save_json(df_cards)
    df_cards.to_csv('cards.csv', index=False)

    if make_artwork:  
        cards = df_cards.drop(labels=['Keyword Abilities', 'Special Abilities', 'Triggers'], axis=1)
        print('Generating artworks...')
        for _, card in tqdm(cards.iterrows()):
            draw_artwork(card)
    
    return


if __name__ == '__main__':

    # Settings
    namesFile = r'.\Names\first_names.txt'
    nb_cards = 50
    plot = True
    make_artwork = True
    random.seed(0)

    NB_KW_ABILITIES = len(KeywordAbilities)
    NB_SP_ABILITIES = len(SpecialAbilities)

    # A larger range corresponds to more byte matches and thus more abilities
    KW_BYTES_RANGE = range(0, 15)
    SP_BYTES_RANGE = range(0, 31)
    TR_BYTES_RANGE = range(0, 15)

    # The higher nb encodings, the more likely byte matches are
    NB_THG_ENC = 24
    NB_POW_ENC = 24
    NB_POINTS_ENC = 8

    ATTRIBUTES_TO_PLOT = ['Power', 'Toughness', 'Points', 'Price', 
                          '# Keyword Abilities', '# Special Abilities', 
                          '# Triggers', '# Relations']

    main()
