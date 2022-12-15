from enum import Enum, auto

class AbilityTriggers(Enum):

    # When NAME
    When_Enters_the_battlefield = auto()
    When_Attacks = auto()
    When_Blocks = auto()
    When_Dies = auto()
    When_Is_put_into_the_discard_pile = auto()
    When_Gets_blocked = auto()

    # Whenever NAME
    Whenever_Becomes_the_target = auto()
    Whenever_Takes_Damage = auto()
    Whenever_Deals_Damage = auto()
    Whenever_Deals_Combat_Damage = auto()
    Whenever_Deals_Damage_To_Player = auto()

    # At the beginning of NO NAME
    Beginning_Phase_DrawI = auto()
    Beginning_Phase_Develop = auto()
    Beginning_Phase_Deploy = auto()
    Beginning_Combat = auto()
    Beginning_Phase_DrawII = auto()
    Beginning_Phase_Recruit = auto()
    Beginning_Phase_Prevail = auto()
    Beginning_When_you_gain_Initiative = auto() # The combat priority (not the MTG one)
