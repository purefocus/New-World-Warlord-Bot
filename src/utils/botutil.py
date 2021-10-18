import discord
from dat.WarDef import *
from dat.EnlistDef import *
from discord_ui import *

import csv
from config import tmpfile

from tabulate import tabulate


async def get_def_war(state, ctx: SlashedCommand):
    war = state.get_modifying_war(ctx.author.name)
    if war is None:
        war = await set_selected_war(state, ctx)

    return war


async def set_selected_war(state, ctx: SlashedCommand):
    print(ctx.author)
    war: WarDef = await select_war(state, ctx, 'Which war are you working with?', allow_multiple=False)
    if war is not None:
        state.set_modifying_war(ctx.author.name, war)
        await ctx.respond(f'Selected war: {war.location}', hidden=True)
        return war
    else:
        await ctx.respond(f'No war selected!', hidden=True)
    return None


async def select_war(state, ctx: SlashedCommand, question, allow_multiple=False):
    select_options = []

    for w in state.wars:
        if state.wars[w].active:
            select_options.append(SelectOption(value=w, label=state.wars[w].location))

    if len(select_options) == 0:
        await ctx.send(content='There are no active wars!', hidden=True)
        return ([], None) if allow_multiple else (None, None)

    msg = await ctx.send(question,
                         components=[
                             SelectMenu('war',
                                        options=select_options,
                                        placeholder='War',
                                        max_values=len(select_options) if allow_multiple else 1)
                         ], hidden=True)

    menu: SelectedMenu = await msg.wait_for('select', state.client, timeout=state.config.question_timeout)

    selected_wars = []
    for selected in menu.selected_values:
        selected_wars.append(state.wars[selected])

    await menu.respond(ninja_mode=True)
    if len(selected_wars) > 0:
        return (selected_wars, msg) if allow_multiple else (selected_wars[0], msg)
    return ([], msg) if allow_multiple else (None, msg)


def create_war_roster(war):
    data = war.create_table()
    file = tmpfile('roster.csv')

    war_info = [
        ['Location', war.location],
        ['Time', war.war_time],
        ['Attacking', war.attacking],
        ['Defending', war.defending],
        [' ', ' ']
    ]

    with open('roster.csv', 'w', encoding='UTF8') as f:
        out = csv.writer(f)
        out.writerows(war_info)
        out.writerows(data)

    return file


def create_text_war_roster(war, filter=None):
    data = war.create_table(filter)

    formatted_roster = tabulate(tabular_data=data[1:], headers=data[0], tablefmt="fancy_grid")

    return formatted_roster


async def add_war_board(war: WarDef, state, update_if_exists=True):
    await state.add_war_board(war, update_if_exists)


async def update_war_boards(war, state):
    await state.update_war_boards(war)


class ChannelReference:

    def __init__(self, ch: discord.TextChannel = None):
        if ch is None:
            self.guild_id = None
            self.channel_id = None
        else:
            self.guild_id = ch.guild.id
            self.channel_id = ch.id

    def as_dict(self):
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
        }

    def from_dict(self, data):
        self.guild_id = data['guild_id']
        self.channel_id = data['channel_id']
        return self

    def get_channel(self, client: discord.Client) -> discord.TextChannel:

        guild: discord.Guild = client.get_guild(self.guild_id)
        channel: discord.TextChannel = guild.get_channel(self.channel_id)

        return channel


class MessageReference:

    def __init__(self, msg=None):
        if msg is None:
            self.guild_id = None
            self.channel_id = None
            self.message_id = None
        else:
            self.guild_id = msg.guild.id
            self.channel_id = msg.channel.id
            self.message_id = msg.id

    def as_dict(self):
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
            'message_id': self.message_id
        }

    def from_dict(self, data):
        self.guild_id = data['guild_id']
        self.channel_id = data['channel_id']
        self.message_id = data['message_id']
        return self

    def get_message(self, client: discord.Client) -> discord.Message:

        guild: discord.Guild = client.get_guild(self.guild_id)
        channel: discord.TextChannel = guild.get_channel(self.channel_id)
        message: discord.Message = channel.get_partial_message(self.message_id)

        return message
