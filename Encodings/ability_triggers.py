from enum import Enum, auto

class AbilityTriggers(Enum):

    # When NAME
    When_enters_the_battlefield = auto()
    When_attacks = auto()
    When_blocks = auto()
    When_dies = auto()
    When_is_put_into_the_discard_pile = auto()
    When_gets_blocked = auto()

    # Whenever NAME
    Whenever_becomes_a_target = auto()
    Whenever_takes_damage = auto()
    Whenever_deals_damage = auto()
    Whenever_deals_combat_damage = auto()
    Whenever_deals_damage_to_a_player = auto()

    # At the beginning of NO NAME
    Beginning_phase_DrawI = auto()
    Beginning_phase_Develop = auto()
    Beginning_phase_Deploy = auto()
    Beginning_combat = auto()
    Beginning_phase_DrawII = auto()
    Beginning_phase_Recruit = auto()
    Beginning_phase_Prevail = auto()
    Beginning_when_you_gain_the_initiative = auto() # The combat priority (not the MTG one)
