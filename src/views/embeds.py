import discord
from database.tables.users_table import UserRow


def user_embed(user: UserRow, state=None):
    embed = discord.Embed(title='War Enlistment')
    user_data = f'*Name*: {user.username} (level {user.level})\n*Faction*: {user.faction}\n*Company*: {user.company}'

    embed.add_field(name='User', value=user_data, inline=False)

    embed.add_field(name='Roles', value=user.role, inline=True)
    embed.add_field(name='Weapons', value=f'{user.weapon1}/{user.weapon2}', inline=True)
    if user.extra is not None:
        embed.add_field(name='Extra Information', value=user.extra, inline=False)

    if state is not None:
        enlisted_wars = ''
        for war in state.wars:
            war = state.wars[war]
            if war.active and user.username in war.roster:
                enlisted_wars += f'> {war.name}\n'
        if len(enlisted_wars) > 0:
            embed.add_field(name='Wars', value=enlisted_wars, inline=False)

    return embed
