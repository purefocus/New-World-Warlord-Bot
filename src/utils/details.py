WEAPON_CHOICES = ['Sword & Shield', 'Rapier', 'Hatchet',  # One handed
                  'Spear', 'Great Axe', 'War Hammer',  # 2 handed
                  'Bow', 'Musket',  # Ranged
                  'Fire Staff', 'Life Staff', 'Ice Gauntlet']  # Magic

WAR_ROLES = ['DPS', 'Healer', 'Tank', 'Siege', 'Sharpshooter']

FACTIONS = ['Syndicate', 'Covenant', 'Marauders']

def add_mapping(mappings, name: str, aliases: list):
    fort_name = f'{name}'
    mappings[name.lower()] = fort_name
    for alias in aliases:
        mappings[alias.lower()] = fort_name


##########################
#  Emoji Role Mappings   #
##########################
role_emoji_mappings = {}
add_mapping(role_emoji_mappings, ':axe:', ['dps'])
add_mapping(role_emoji_mappings, ':adhesive_bandage:', ['healer', 'heal'])
add_mapping(role_emoji_mappings, ':shield:', ['tank'])
add_mapping(role_emoji_mappings, ':hammer_pick:', ['siege'])
add_mapping(role_emoji_mappings, ':bow_and_arrow:', ['sharpshooter', 'ranged', 'musket'])
add_mapping(role_emoji_mappings, ':crown:', ['leader', 'lead'])

##########################
# Location Name Mappings #
##########################
location_mappings = {}
add_mapping(location_mappings, 'Fort First Light', ['First Light', 'firstlight', 'FL'])
add_mapping(location_mappings, 'Fort Monarch\'s Bluff',
            ['Monarch\'s Bluff', 'MB', 'monarchs bluff', 'monarchs', 'bluff'])
add_mapping(location_mappings, 'Fort Brightwood', ['Brightwood', 'BW', 'blight'])
add_mapping(location_mappings, 'Fort Weaver\'s Fen', ['Weaver\'s Fen', 'weavers fen', 'WF', 'weavers'])
add_mapping(location_mappings, 'Fort Mourningdale', ['MD', 'mourningdale', 'morningdale'])
add_mapping(location_mappings, 'Fort Everfall', ['Everfall', 'EF'])
add_mapping(location_mappings, 'Fort Cutlass Keys', ['Cutlass Keys', 'CK', 'cutlass'])
add_mapping(location_mappings, 'Fort Restless Shores', ['Restless Shores', 'RS', 'restless', 'shores'])
add_mapping(location_mappings, 'Fort Ebonscale Reach', ['Ebonscale Reach', 'ER', 'ebonscale', 'reach'])
add_mapping(location_mappings, 'Fort Reekwater', ['Reekwater', 'RW', 'reek'])
add_mapping(location_mappings, 'Fort Windsward', ['Windsward', 'WW'])


def get_location(loc):
    _loc = loc.lower()
    if _loc in location_mappings:
        return location_mappings[_loc]
    return loc


def role_emoji(role):
    _loc = role.lower()
    if _loc in role_emoji_mappings:
        return role_emoji_mappings[_loc]
    return role


def replace_emojis(txt: str):
    _txt = txt.lower()
    for emoji in role_emoji_mappings:
        _txt = _txt.replace(emoji, role_emoji_mappings[emoji])
    if _txt != txt.lower():
        return _txt
    return txt
