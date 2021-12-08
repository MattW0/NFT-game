from enum import Enum, auto

class AbilityTriggers(Enum):
    ETB = auto()
    Attack = auto()
    Takes_Damage = auto()
    Deals_Damage = auto()
    Deals_Damage_To_Player = auto()
    Beginning_of_Upkeep = auto()
    Beginning_of_Main = auto()
    Beginning_of_Combat = auto()
    Beginning_of_Endstep = auto()