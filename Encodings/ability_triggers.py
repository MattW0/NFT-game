from enum import Enum, auto

class AbilityTriggers(Enum):
    ETBs = auto()
    Attacks = auto()
    Blocks = auto()
    Dies = auto()
    Is_put_into_discard = auto()
    Is_targeted = auto()
    Takes_Damage = auto()
    Deals_Damage = auto()
    Deals_Combat_Damage = auto()
    Deals_Damage_To_Player = auto()
    Beginning_of_Phase_X = auto()
    Beginning_of_Combat = auto()
    Gaining_Initiative = auto()
