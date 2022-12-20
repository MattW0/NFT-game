from enum import Enum, auto

class SpecialAbilities(Enum):
    # Abilitites are ordered by "strength" (in terms of what is strongest in game -> hard to evaluate)

    # With X -> X needs to be differently distributed probably:
    gain_X_life = auto()
    mill_X = auto()
    scry_X = auto()

    # With X and special
    Put_X_Marker_marker_on_target_creature = auto() # Each kind of KW marker and +1/+1
    create_X_treasure_token = auto()
    create_X_creature_token = auto() # What kind of creature token?

    # With target
    deal_X_damage_to_target_creature = auto()
    destroy_target_creature = auto() # expensive
    exile_target_creature = auto() # Expensive!
