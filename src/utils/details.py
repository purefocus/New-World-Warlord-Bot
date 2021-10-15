location_mappings = {

}


def add_mapping(name: str, aliases: list):
    fort_name = f'Fort {name}'
    location_mappings[name.lower()] = fort_name
    for alias in aliases:
        location_mappings[alias.lower()] = fort_name


add_mapping('First Light', ['FL'])
add_mapping('Monarch\'s Bluff', ['MB', 'monarchs bluff', 'monarchs', 'bluff'])
add_mapping('Brightwood', ['BW', 'blight'])
add_mapping('Weaver\'s Fen', ['WF', 'weavers'])
add_mapping('Mourningdale', ['MD', 'mourningdale'])
add_mapping('Everfall', ['EF'])
add_mapping('Cutlass Keys', ['CK', 'cutlass'])
add_mapping('Restless Shores', ['RS', 'restless', 'shores'])
add_mapping('Ebonscale Reach', ['ER', 'ebonscale', 'reach'])
add_mapping('Reekwater', ['RW', 'reek'])
add_mapping('Windsward', ['WW'])


def get_location(loc):
    _loc = loc.lower()
    if _loc in location_mappings:
        return location_mappings[_loc]
    return loc
