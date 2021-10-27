import asyncio
import discord
from dat.EnlistDef import *
# from dat.WarStrategy import *
from dat.WarDef import *
from discord_ui import *

from config import *
from utils.botutil import *
from utils.pdfgen import generate_enlistment_pdf
# from utils.enlistment_utils import *
from bot_state import BotState
from views.roster import create_roster_embed


async def cmd_war_select(state, ctx):
    await set_selected_war(state, ctx)


async def cmd_get_enlisted(state: BotState, ctx):
    war, _ = await select_war(state, ctx, 'Select the war to get the enlistment roster for',
                              allow_multiple=False,
                              allow_overall=True)
    if war is not None:
        title = str(war)

        # embed = discord.Embed(title='Enlistment Roster')
        # embed.set_author(name=war.location)
        # roster = create_text_war_roster(war, state.users)
        # print(len(roster))
        # embed.add_field(name='roster', value=f'```{roster}```')

        if isinstance(war, WarDef):
            names = war.roster
        else:
            names = state.users.users.keys()

        embed = create_roster_embed(names, state, title)
        await ctx.send(content='Here\'s the roster.', embed=embed)
        # print_dict(by_roles)
        # create_war_roster(war)
        #

        # await ctx.send(content=f"```\n{roster}\n```", hidden=True)
    else:
        await ctx.respond(content=f"Denied!", hidden=True)


async def cmd_dl_enlisted(state, ctx):
    war, _ = await select_war(state, ctx, 'Select the war to get the enlistment roster for', allow_multiple=False)
    if war is not None:
        file = generate_enlistment_pdf(war, state.users)
        await ctx.send(content='Here\'s the roster.', file=discord.File(file), hidden=True)
        # file = create_war_roster(war)
        # await ctx.send(content='Here\'s the roster.', file=discord.File(file), hidden=True)
    else:
        await ctx.send(content=f"Denied!")
