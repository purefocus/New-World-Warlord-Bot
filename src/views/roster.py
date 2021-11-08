from dat.EnlistDef import Enlistment
from utils.userdata import UserData
from utils.details import WAR_ROLES

from discord import Embed


def _get_users_from_names(names, users: UserData):
    return [users[name] for name in names]


def _group_by_role(roster: list):
    result = {}

    for role in WAR_ROLES:
        result[role] = []
        for user in roster:
            if user is None:
                continue

            if role in user.roles:
                result[role].append(user)

    return result


def create_roster_embed(names, state, title=None, embed=None):
    roster = _get_users_from_names(names, state.users)
    groups = _group_by_role(roster)
    if embed is None:
        embed = Embed(title='War Enlistment', description=f'{title}')

    for key in groups:
        value = ''
        enlisted = groups[key]
        enlisted = sorted(enlisted, key=lambda x: x.level, reverse=True)
        idx = 0
        for enl in enlisted:
            enl: Enlistment = enl
            val = '\t' + str(enl) + '\n'
            if len(value) + len(val) > 1024:
                embed.add_field(name=f'{key} {"" if idx == 0 else idx}', value=value, inline=False)
                value = ''
                idx += 1
            value += val

        if value != '':
            embed.add_field(name=f'{key} {"" if idx == 0 else idx}', value=value, inline=False)

    # embed.set_footer(text='Generated by /get_enlisted')

    return embed
