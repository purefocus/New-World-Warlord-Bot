WEAPON_CHOICES = ['Sword & Shield', 'Rapier', 'Hatchet',  # One handed
                  'Spear', 'Great Axe', 'War Hammer',  # 2 handed
                  'Bow', 'Musket',  # Ranged
                  'Fire Staff', 'Life Staff', 'Ice Gauntlet', 'Void Gauntlet']  # Magic

WEAPON_CHOICES_ABRV = ['SS', 'R', 'H',  # One handed
                       'Sp', 'GA', 'WH',  # 2 handed
                       'Bow', 'M',  # Ranged
                       'FS', 'LS', 'IG', 'VG']  # Magic

WAR_ROLES = ['Healer', 'Tank', 'Dex DPS', 'Str DPS', 'Int DPS']

FACTIONS = ['Syndicate', 'Covenant', 'Marauders']


def add_mapping(mappings, name: str, aliases: list):
    fort_name = f'{name}'
    mappings[name.lower()] = fort_name
    for alias in aliases:
        mappings[alias.lower()] = fort_name


##########################
#    Weapon Mappings     #
##########################
weapon_mappings = {}
add_mapping(weapon_mappings, 'Sword & Shield',
            ['Sword and Shield', 'Sword and board', 'word & board', 'Sword&Shield', 'SS'])
add_mapping(weapon_mappings, 'War Hammer', ['Hammer', 'WH', 'Great Hammer', 'GH'])
add_mapping(weapon_mappings, 'Great Axe', ['GA', 'War Axe', 'Axe'])

##########################
#  Emoji Role Mappings   #
##########################
role_emoji_mappings = {}
add_mapping(role_emoji_mappings, ':axe:', ['dps'])
add_mapping(role_emoji_mappings, ':adhesive_bandage:', ['healer', 'heal'])
add_mapping(role_emoji_mappings, ':shield:', ['tank'])
add_mapping(role_emoji_mappings, ':hammer_pick:', ['siege'])
add_mapping(role_emoji_mappings, ':bow_and_arrow:', ['sharpshooter', 'ranged', 'musket', 'dex'])
add_mapping(role_emoji_mappings, ':crown:', ['leader', 'lead'])
add_mapping(role_emoji_mappings, ':man_mage:', ['mage'])
add_mapping(role_emoji_mappings, ':muscle:', ['str dps'])
add_mapping(role_emoji_mappings, ':man_mage:', ['int dps'])
add_mapping(role_emoji_mappings, ':dagger:', ['dex dps'])

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

#########################
# Company Name Mappings #
#########################
company_mappings = {}
add_mapping(company_mappings, 'Lotus Trading',
            ['Lotus Trading Cartel', 'Lotus Trading Company', 'Lotus Holdings Co.', 'LTC'])


def get_location(loc):
    if loc is None:
        return None
    _loc = loc.lower()
    if _loc in location_mappings:
        return location_mappings[_loc]
    return loc


def role_emoji(role):
    if role is None:
        return None
    _loc = role.lower()
    if _loc in role_emoji_mappings:
        return role_emoji_mappings[_loc]
    return role


def replace_weapon(weappon):
    if weappon is None:
        return None
    _weappon = weappon.lower()
    if _weappon in weapon_mappings:
        return weapon_mappings[_weappon]
    return weappon


def replace_emojis(txt: str):
    if txt is None:
        return None
    _txt = txt.lower()
    for emoji in role_emoji_mappings:
        _txt = _txt.replace(emoji, role_emoji_mappings[emoji])
    if _txt != txt.lower():
        return _txt
    return txt


def replace_weapons_abbrev(txt: str):
    for i in range(len(WEAPON_CHOICES)):
        txt = txt.replace(WEAPON_CHOICES[i], WEAPON_CHOICES_ABRV[i])
    return txt


def replace_company_name(company: str):
    if company is None:
        return None
    company = company.lower()
    if company in company_mappings:
        return company_mappings[company]
    return company


import datetime


def _parse_date(text, format):
    try:
        dt = datetime.datetime.strptime(text, format)
        now = datetime.datetime.now()
        dt = dt.replace(year=now.year, tzinfo=now.tzinfo)
        if dt.hour < 12:
            dt = dt.replace(hour=dt.hour + 12)
        return dt
    except:
        # import traceback
        # import sys
        #
        # traceback.print_exception(*sys.exc_info())
        pass
    return None


def parse_date(text):
    formats = [
        '%a, %b %d, %H:%M%p %Z',  # Tue, Nov 30, 11:00PM EST
        '%a, %b %d, %H:%M %p %Z',  # Tue, Nov 30, 11:00 PM EST
        '%a, %b %d, %H:%M %p',  # Tue, Nov 30, 11:00 PM
        '%b %d @ %H:%M %p',  # Nov 30 @ 11:00 PM
        '%m/%d %H:%M %p %Z',  # 11/30 11:00 PM EST
    ]
    for fmt in formats:
        result = _parse_date(text, fmt)
        if result is not None:
            return result
            # ts = int(result.timestamp())
            # return f'<t:{ts}:f> (<t:{ts}:R>)'

    return text


'''
Use <t:TIMESTAMP:FLAG> to send it

Available flags:

    t: Short time (e.g 9:41 PM)

    T: Long Time (e.g. 9:41:30 PM)

    d: Short Date (e.g. 30/06/2021)

    D: Long Date (e.g. 30 June 2021)

    f (default): Short Date/Time (e.g. 30 June 2021 9:41 PM)

    F: Long Date/Time (e.g. Wednesday, June, 30, 2021 9:41 PM)

    R: Relative Time (e.g. 2 months ago, in an hour)
'''
