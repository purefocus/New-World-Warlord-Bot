import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

from utils.botutil import *
from utils.pdfgen import *
from bot_state import BotState
from views.roster import create_roster_embed
import discord_ui
from discord_ui import SlashOption, SlashPermission, SlashedCommand
from discord_ui import Interaction
from views.weapon_selection import ask_weapon_mastery
from views.view_confirm import ask_confirm

from utils.botutil import print_stack_trace
from utils.discord_utils import *
import pandas as pd
import os
from utils.colorprint import *

import config as cfg


class RosterCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='get_enlisted',
               description='Replies with a table of all the users enlisted for a specific war',
               **cfg.cmd_cfg)
    async def get_enlisted(self, ctx):
        war, _ = await select_war(state, ctx, 'Select the war to get the enlistment roster for',
                                  allow_multiple=False,
                                  allow_overall=True)
        if war is not None:
            title = str(war)

            if isinstance(war, WarDef):
                names = war.roster
            else:
                names = self.state.users.users.keys()

            embed = create_roster_embed(names, self.state, title, abrv_line=False)
            await ctx.send(content='Here\'s the roster.', embed=embed)

        else:
            await ctx.respond(content=f"Denied!", hidden=True)

    @slash_cog(
        name='download_enlisted',
        description='Generates a CSV file with a table of everyone who signed up (Can be imported into excel).',
        **cfg.cmd_cfg)
    async def download_enlisted(self, ctx):
        war, _ = await select_war(self.state, ctx, 'Select the war to get the enlistment roster for',
                                  allow_multiple=False)
        if war is not None:

            file = generate_enlistment_csv(war, self.state.users)

            await ctx.send(content='Here\'s the roster.', file=discord.File(file), hidden=True)
        else:
            await ctx.send(content=f"Denied!")

    @slash_cog(name='end_war',
               description='Flags a war as ended, disabling the ability to sign up for it',
               **cfg.cmd_cfg_mod)
    async def end_war(self, ctx):
        war, msg = await select_war(self.state, ctx, 'Select the war to end', allow_multiple=False)
        if war is not None:
            war.active = False
            await msg.edit(content=f'War \'{war.location}\' has been ended!', components=None)
            for board in war.boards:
                try:
                    m = await board.get_message(self.state.client)
                    if m is not None:
                        await m.delete()
                except:
                    pass
            self.state.save_war_data()

    @slash_cog(name='repost_war',
               description='Reposts the war notification',
               **cfg.cmd_cfg_elev)
    async def repost_war(self, ctx):
        wars, _ = await select_war(self.state, ctx, 'Select war', allow_multiple=True)
        for war in wars:
            for board in war.boards:
                try:
                    msg = await board.get_message(self.state.client)
                    if msg is not None:
                        await msg.delete()
                    board.valid = False
                except:
                    pass
            await add_war_board(war, self.state)
            self.state.save_war_data()

    @slash_cog(name='post_war',
               description='posts a war notification in your current channel',
               **cfg.cmd_cfg_elev)
    async def post_war(self, ctx):
        wars, _ = await select_war(self.state, ctx, 'Select war', allow_multiple=True)
        for war in wars:
            await add_war_board_to(war, self.state, ctx.channel)
            self.state.save_war_data()

    @slash_cog(name='post_enlist',
               description='posts a war enlistment button in your current channel',
               **cfg.cmd_cfg_elev)
    async def post_enlist(self, ctx):
        wars, msg = await select_war(self.state, ctx, 'Select war', allow_multiple=True)
        btns = []
        for war in wars:
            btns.append(
                Button(
                    custom_id=f'btn:enlist:{war.id}',
                    label=f'Enlist for {war.location}',
                    new_line=True
                )
            )
        await msg.edit(content='Done!', components=None)
        await ctx.respond(content='**Click buttons to enlist!**', components=btns)
