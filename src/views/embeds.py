import discord
from database.tables.users_table import UserRow

from utils.details import parse_date


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


def get_embeded(war):
    if war.name is not None:
        embed = discord.Embed(title=f':exclamation: __{war.name}!__ :exclamation: ',
                              colour=discord.Colour.blurple())
    else:
        embed = discord.Embed(title=f':exclamation: __{war.location}!__ :exclamation: ',
                              colour=discord.Colour.blurple())
    # embed.set_author(name='Test')
    if war.image_url is not None:
        embed.set_image(url=war.image_url)
    # else:

    wartime = parse_date(war.war_time)
    if wartime is None:
        wartime = ''
    if not isinstance(wartime, str):
        ts = int(wartime.timestamp())
        wartime = f'<t:{ts}:f> (<t:{ts}:R>)'
    if war.name is None:
        embed.add_field(name='Details',
                        value=f'📆 {wartime}\n📣 {war.owners}',
                        inline=False)
    else:
        embed.add_field(name='Details',
                        value=f'📆 {wartime}\n📣 {war.owners}\n📍 {war.location}',
                        inline=False)
    if war.attacking is not None:
        # embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W_400x400.jpg')
        embed.add_field(name='Attackers', value=f'{war.attacking}', inline=True)
        embed.add_field(name='Defenders', value=war.defending, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=False)

        # self.groups.embed(embed)

    # if self.looking_for is not None:
    #     embed.add_field(name='Looking for', value=self.looking_for, inline=False)

    if war.additional_info is not None:
        info = war.additional_info
        if len(info) >= 1018:
            info = war.additional_info[:1018]
        embed.add_field(name='Additional Info', value=f'```{info}```', inline=False)

    # embed.add_field(name='\u200b', value='\u200b', inline=False)
    embed.add_field(name='Enlisted',
                    value=f'{str(len(war.roster))}',
                    inline=True)
    embed.add_field(name='Absent',
                    value=f'{str(len(war.absent))}',
                    inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True)

    if war.private is not None:
        embed.set_footer(text='🔒 Private')

    # embed.set_footer(text='Use /enlist to sign up!')

    # embed.set_footer(text=f'\nID: {self.id}')

    return embed
