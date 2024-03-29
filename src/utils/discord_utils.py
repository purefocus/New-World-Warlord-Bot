import discord
import utils.botutil as bu

import re

_MENTION_REGEX_ = re.compile(r'<@(&?[0-9]*)>')

_COMPANY_ROLE_COLOR_ = discord.Colour(0xb9adff)
_COMPANY_RANK_NAMES_ = ['Governor', 'Consul', 'Officer']

special_company_role_cases = {
    868924409115709480: {  # Lotus Trading Company
        'Member': 'Lotus Trading'
    }
}


def _get_company_role_special(user: discord.Member) -> [None, str]:
    gid = user.guild.id
    if gid in special_company_role_cases:
        cases = special_company_role_cases[gid]
        for key in cases:
            if has_role(user, key):
                return cases[key]
    return None


def has_role(user: discord.Member, role_name):
    if isinstance(role_name, str):
        for role in user.roles:
            if role.name == role_name:
                return True
    elif isinstance(role_name, int):
        for role in user.roles:
            if role.id == role_name:
                return True
    return False


def get_company_role(user: discord.Member):
    # Add case for lotus

    role = _get_company_role_special(user)
    if role is not None:
        return role

    for role in user.roles:
        if role.color == _COMPANY_ROLE_COLOR_:
            return role.name
    return None


def is_verified(user: discord.Member):
    return has_role(user, 'Verified')


def get_rank(user: discord.Member):
    for role in user.roles:
        if role.name in _COMPANY_RANK_NAMES_:
            return role.name
    return 'Settler'


async def get_verified_users(guild: discord.Guild):
    users = []
    # members = guild.fetch_members()
    role: discord.Role = guild.get_role(895466455766802442)
    # members = guild.members
    members = role.members
    for user in members:
        name = user.display_name
        company = get_company_role(user)
        rank = None if company is None else get_rank(user)
        users.append([name, company, rank])

    users = sorted(users, key=lambda x: x[0])

    return users


def find_company_role(guild: discord.Guild, role_name):
    if role_name is None:
        return None
    role_name = role_name.lower()
    for role in guild.roles:
        if role.name.lower() == role_name and role.color == _COMPANY_ROLE_COLOR_:
            return role
    return None


async def get_companies(guild: discord.Guild):
    companies = {
        '': {'members': [], 'Consul': [], 'Officer': [], 'Governor': [], 'Settler': []}
    }
    try:

        for user in guild.members:
            if not is_verified(user):
                continue

            company = get_company_role(user)
            if company is None:
                companies['']['members'].append(user)
            else:
                if company not in companies:
                    companies[company] = {'members': [], 'Consul': [], 'Officer': [], 'Governor': [], 'Settler': []}
                companies[company]['members'].append(user.display_name)
                rank = get_rank(user)
                companies[company][rank].append(user.display_name)
    except Exception as e:
        bu.print_stack_trace()

    return companies


def resolve_mention(txt: str, guild: discord.Guild):
    matched = _MENTION_REGEX_.findall(txt)
    for m in matched:
        if m[0] == '&':
            return guild.get_role(int(m[1:]))
        return guild.get_member(int(m))
    return None


def get_embed_field(embed: discord.Embed, key):
    for field in embed.fields:
        if field.name == key:
            return field.value
    return None


def add_or_edit_embed_field(embed: discord.Embed, name, value, append=False):
    field_idx = -1
    for i in range(len(embed.fields)):
        field = embed.fields[i]
        if field.name == name:
            field_idx = i
            if field.value == '\u200b':
                break
            if append:
                value = f'{field.value}\n{value}'
            break
    if field_idx == -1:
        embed.add_field(name=name, value=value)
    else:
        embed.set_field_at(field_idx, name=name, value=value)


def handle_mutations(inp: str):
    inp = inp.replace('1', 'L').replace('l', 'L').replace('i', 'L')
    inp = inp.replace('o', 'O').replace('0', 'O')
    inp = inp.replace('s', 'S').replace('5', 'S')
    inp = inp.replace(' ', '').strip()

    return inp


def check_for_matching_name(name: str, guild: discord.Guild):
    matched = []
    name = handle_mutations(name).lower()
    for member in guild.members:
        mut_name = handle_mutations(member.display_name).lower()
        if mut_name == name:
            matched.append(member)

    return matched


def search_for_duplicate_names(guild: discord.Guild):
    matches = {}
    matched = []

    for member in guild.members:
        name = member.display_name
        name_key = handle_mutations(name).lower()
        if name_key in matches:
            matches[name_key].append(member)
            matched.append(name_key)
        else:
            matches[name_key] = [member]

    return [(key, matches[key]) for key in matched]
