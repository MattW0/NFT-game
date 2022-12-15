from enum import Enum, auto

class SpecialAbilities(Enum):
    
    # With X and special
    Put_X_Marker_marker_on_target_creature = auto() # Each kind of KW marker and +1/+1
    Create_X_creature_Token = auto() # What kind of creature token?
    Create_X_treasure_Token = auto()
    
    # With X -> X needs to be differently distributed probably:
    #   Mill/Scry << Create X creatures ...
    Mill_X = auto()
    Scry_X = auto()
    Gain_X_HP = auto()

    # With target
    Exile_target_creature = auto()
    Destroy_target_creature = auto()
    Deal_X_damage_to_target_creature = auto()
