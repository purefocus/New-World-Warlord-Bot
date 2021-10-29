from bot_state import BotState
from utils.details import WEAPON_CHOICES, WEAPON_CHOICES_ABRV
from views.select_menu import selection
from utils.colorprint import print_dict


async def ask_weapon_mastery(state: BotState, ctx):
    selected, msg = await selection(state, ctx,
                               'What weapons do you have a mastery of (*level 15+*) and are comfortable using?',
                               WEAPON_CHOICES, allow_multiple=True)

    weapon_checks = [weapon in selected for weapon in WEAPON_CHOICES]

    test = {}
    for i in range(len(weapon_checks)):
        test[WEAPON_CHOICES_ABRV[i]] = weapon_checks[i]
    print_dict(test)

    return weapon_checks
