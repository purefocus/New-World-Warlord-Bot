import discord

_COMPANY_ROLE_COLOR_ = discord.Colour(0xb9adff)
_COMPANY_RANK_NAMES_ = ['Governor', 'Consul', 'Officer']


def has_role(user: discord.Member, role_name: str):
    for role in user.roles:
        if role.name == role_name:
            return True
    return False


def get_company_role(user: discord.Member):
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
