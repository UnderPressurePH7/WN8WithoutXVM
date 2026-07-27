from constants import ARENA_GUI_TYPE, ARENA_BONUS_TYPE


def _enum_values(enum_cls, names):
    """Return existing enum values without dropping a legitimate numeric zero."""
    values = []
    for name in names:
        value = getattr(enum_cls, name, None)
        if value is not None:
            values.append(value)
    return frozenset(values)


# Supported UI families:
# - Classic: random and clan/stronghold battles
# - Comp7: Onslaught and its tournament/training/light variants
# - Epic Random: Frontline
ALLOWED_GUI_TYPES = _enum_values(ARENA_GUI_TYPE, (
    'RANDOM',
    'STRONGHOLD_BATTLES',
    'SORTIE',
    'FORT_BATTLE',
    'EPIC_BATTLE',
))

ALLOWED_BONUS_TYPES = _enum_values(ARENA_BONUS_TYPE, (
    'REGULAR',
    'RANDOM_NP2',
    'SORTIE_2',
    'FORT_BATTLE_2',
    'COMP7',
    'TOURNAMENT_COMP7',
    'TRAINING_COMP7',
    'COMP7_LIGHT',
    'EPIC_RANDOM',
    'EPIC_RANDOM_2',
))


def is_supported(arena):
    if arena is None:
        return False

    gui_type = getattr(arena, 'guiType', None)
    bonus_type = getattr(arena, 'bonusType', None)

    if gui_type is not None and gui_type in ALLOWED_GUI_TYPES:
        return True
    if bonus_type is not None and bonus_type in ALLOWED_BONUS_TYPES:
        return True
    return False
