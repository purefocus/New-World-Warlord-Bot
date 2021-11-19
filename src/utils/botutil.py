import discord
from dat.WarDef import *
from dat.EnlistDef import *
from discord_ui import *

import csv
from config import tmpfile

from tabulate import tabulate
import traceback
import sys


def print_stack_trace():
    traceback.print_exception(*sys.exc_info())


async def get_def_war(state, ctx: SlashedCommand):
    war = state.get_modifying_war(ctx.author.name)
    if war is None:
        war = await set_selected_war(state, ctx)

    return war


async def set_selected_war(state, ctx: SlashedCommand):
    print(ctx.author)
    war, _ = await select_war(state, ctx, 'Which war are you working with?', allow_multiple=False)
    if war is not None:
        state.set_modifying_war(ctx.author.name, war)
        await ctx.respond(f'Selected war: {war.location}', hidden=True)
        return war
    else:
        await ctx.respond(f'No war selected!', hidden=True)
    return None


async def select_war(state, ctx: SlashedCommand, question, allow_multiple=False, allow_overall=False):
    select_options = []
    if allow_overall:
        select_options.append(SelectOption(value='global_roster', label='Global Roster', description=str(state.users)))

    for w in state.wars:
        war = state.wars[w]
        if war.active:
            select_options.append(SelectOption(value=w, label=war.location, description=war.make_description()))

    if len(select_options) == 0:
        await ctx.send(content='There are no active wars!', hidden=True)
        return ([], None) if allow_multiple else (None, None)

    msg = await ctx.send(question,
                         components=[
                             SelectMenu('war',
                                        options=select_options,
                                        placeholder='Select a War',
                                        max_values=len(select_options) if allow_multiple else 1)
                         ], hidden=True)

    menu: SelectedMenu = await msg.wait_for('select', state.client, timeout=state.config.question_timeout)

    selected_wars = []
    for selected in menu.selected_values:
        if selected == 'global_roster':
            selected_wars.append('Global Roster')
        else:
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


def create_text_war_roster(war: WarDef, users, filter=None):
    data = war.create_table(users, filter)

    formatted_roster = tabulate(tabular_data=data[1:], headers=data[0])  # , tablefmt="fancy_grid"

    return formatted_roster


async def add_war_board(war: WarDef, state, reply_msg=None):
    await state.add_war_board(war, reply_msg)


async def add_war_board_to(war: WarDef, state, channel):
    await state.add_war_board_to(war, channel)


async def update_war_boards(war, state):
    await state.update_war_boards(war)

# def load_message_references(self, data: dict, key: str):
#
#     result = []
#     if key in data:
#         data = data[key]
#
#         if isinstance(data, dict):
#             for k in data:
#
#     return result
