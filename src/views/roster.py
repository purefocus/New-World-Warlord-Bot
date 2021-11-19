from dat.EnlistDef import Enlistment
from utils.userdata import UserData
from utils.details import WAR_ROLES

from discord import Embed


def _get_users_from_names(names, absent, users: UserData):
    if absent is None:
        absent = []
    return [users[name] for name in names], [users[name] for name in absent]


def _group_by_role(roster: list, absent: list):
    result = {}

    for role in WAR_ROLES:
        result[role] = []
        for user in roster:
            if user is None:
                continue

            if role in user.roles:
                result[role].append(user)
    result['🚫 Absent'] = absent
    return result


def create_roster_embed(names, absent, state, title=None, embed=None, abrv_line=False):
    roster, absent = _get_users_from_names(names, absent, state.users)
    groups = _group_by_role(roster, absent)
    if embed is None:
        embed = Embed(title='War Enlistment', description=f'{title}')
    fc = 0
    for key in groups:
        value = ''
        enlisted = groups[key]
        # enlisted = sorted(enlisted, key=lambda x: x.level, reverse=True)
        idx = 0
        for enl in enlisted:
            enl: Enlistment = enl
            if enl is None:
                continue
            val = '> ' + str(enl.roster_line(abrv_line)) + '\n'
            if len(value) + len(val) > 1024:
                embed.add_field(name=f'{key} {"" if idx == 0 else idx}', value=value, inline=abrv_line)
                value = ''
                idx += 1

                if fc % 2 == 1 and abrv_line:
                    embed.add_field(name='\u200b', value='\u200b')
                fc += 1
            value += val

        if value != '':
            embed.add_field(name=f'{key} {"" if idx == 0 else idx}', value=value, inline=abrv_line)

            if fc % 2 == 1 and abrv_line:
                embed.add_field(name='\u200b', value='\u200b')
            fc += 1

    # embed.set_footer(text='Generated by /get_enlisted')

    return embed
