import random
import numpy as np

from Encodings.keyword_abilities import KeywordAbilities

POISSON_DIST = list(np.random.poisson(0.5, 1000) + 1)
MARKERS = [e.name for e in KeywordAbilities]

# 1/3 chance of getting a +1/+1 marker instead of keyword marker
for i in range(round(len(MARKERS)/3)):
    MARKERS.append('+1/+1')


def relate_triggers_and_special_abilities(df_cards):
    # Relates triggers to special abilities
    
    relations = []
    texts = []
    for card in df_cards.iterrows():

        name = card[1]['Name']
        triggers = card[1]['Triggers']
        special_abilities = card[1]['Special Abilities']

        card_relations = construct_relations(special_abilities, triggers)
        relations.append(card_relations)

        card_texts = []
        for rel in card_relations:
            text = construct_string(name, rel)
            card_texts.append(text)
        texts.append(card_texts)

    df_cards["Relations"] = relations
    df_cards["# Relations"] = [len(lst) for lst in relations]
    df_cards["Relation text"] = texts

    return df_cards


def evaluate_keywords(df_cards):

    for card in df_cards.iterrows(): 

        keywords = card[1]['Keyword Abilities']
        for kw in keywords:
            if (kw == 'Attacker'):
                # check if attack > 0, if not drop ability
                # Decrease price
                pass
            elif (kw == 'Defender'):
                # Decrease price
                pass
            elif (kw == 'Indestructible'):
                # Increase price 
                pass
            elif (kw == 'Vigilance'):
                # check if attack > 0, if not decrease price
                pass
            elif (kw == 'Protection'):
                # Protection from what?
                # Maybe increase price
                pass
    
    return df_cards


def construct_relations(special_abilities, triggers):
    relations = []

    if len(triggers) == 0 or len(special_abilities) == 0:
        return []

    for sp_ab in special_abilities:
        relations.append({triggers[0]: sp_ab})
        triggers.pop(0)
        if len(triggers) == 0:
            break

    return relations


# I should do the string construction in Unity but decide on special includes here (X, Marker, ..)
def construct_string(name, relation):
    
    txt = ''

    # Trigger
    trig = list(relation.keys())[0]
    time, occurence = trig.split('_', 1)
    if (time == 'Beginning'):
        phase = occurence.split('_')[-1]
        if (phase == 'initiative'):
            txt += 'When you gain the initiative, '
        else:
            txt += f'At the beginning of {phase}, '
    elif (time == 'When' or time == 'Whenever'):
        occurence = occurence.replace('_', ' ')
        txt += f'{time} {name} {occurence}, '

    # Special Ability
    sp_ab = list(relation.values())[0]
    if (sp_ab.__contains__('Marker')):
        marker = random.choice(MARKERS) # need to make this deterministic
        if (marker == '+1/+1'):
            sp_ab = sp_ab.replace('Marker', marker)
        else:
            sp_ab = sp_ab.replace('X_Marker', f'a_{marker}')
    if (sp_ab.__contains__('X')):
        x = random.choice(POISSON_DIST) # need to make this deterministic
        sp_ab = sp_ab.replace('X', str(x))
    
    sp_ab = sp_ab.replace('_', ' ')
    txt += sp_ab

    return txt


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