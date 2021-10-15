location_mappings = {

}


def add_mapping(name: str, aliases: list):
    fort_name = f'Fort {name}'
    location_mappings[name.lower()] = fort_name
    for alias in aliases:
        location_mappings[alias.lower()] = fort_name


add_mapping('First Light', ['FL'])
add_mapping('Monarch\'s Bluff', ['monarchs bluff', 'monarchs', 'MB', 'bluff'])
add_mapping('Blightwood', ['BW', 'blight'])
add_mapping('Weaver\'s Fen', ['WF', 'weavers'])
add_mapping('Mourningdale', ['mourningdale'])




def get_location(loc):
    _loc = loc.lower()
    if _loc in location_mappings:
        return location_mappings[_loc]
    return loc

print(location_mappings)

print(get_location('Mourningdale'))
print(get_location('mourningdale'))