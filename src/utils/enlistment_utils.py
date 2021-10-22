from dat.WarDef import WarDef
from dat.EnlistDef import Enlistment
from utils.details import WAR_ROLES
from utils.userdata import UserData

from discord import Embed


def create_enlistment_embed(war, state, group_by):
    results = {}
    if group_by == 'roles':
        results = get_enlisted_by_roles(war, state.users)

    embed = Embed(title='War Enlistment', description=f'{war.location}')
    embed.set_author(name=f'Grouped by {group_by}')

    for key in results:
        value = ''
        enlisted = results[key]
        enlisted = sorted(enlisted, key=lambda x: x.level, reverse=True)
        idx = 0
        for enl in enlisted:
            enl: Enlistment = enl
            val = '\t' + str(enl) + '\n'
            if len(value) + len(val) > 1024:
                embed.add_field(name=f'{key}s {"" if idx == 0 else idx}', value=value, inline=False)
                value = ''
                idx += 1
            value += val

        if value == '':
            value = '-'

        embed.add_field(name=f'{key}s {"" if idx == 0 else idx}', value=value, inline=False)

    embed.set_footer(text='Generated by /get_enlisted')

    return embed


def get_enlisted_by_roles(war: WarDef, users: UserData):
    print(type(war))
    result = {}
    for role in WAR_ROLES:
        lst = []

        for enl in war.roster:
            enl: Enlistment = users[enl]
            if role in enl.roles:
                lst.append(enl)

        result[role] = lst

    return result
