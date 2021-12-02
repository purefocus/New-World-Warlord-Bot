import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

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


class BotManagementCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState, ui: discord_ui.UI):
        self.client = client
        self.state = state
        self.ui = ui

    @slash_cog(name='warlord_cmd_sync')
    async def warlord_cmd_sync(self, ctx: SlashedCommand, nuke=True):
        try:
            if ctx.author.id == 198526201374048256:
                msg = await ctx.send(content='Removing all Commands... ', hidden=True)
                if nuke:
                    await self.ui.slash.nuke_commands()
                await msg.edit(content=f'{msg.content}\nAdding Commands...')
                print('Commands Before: ', self.state.client.commands)
                await self.ui.slash.sync_commands()
                print('Commands After: ', self.state.client.commands)
                await msg.edit(content=f'{msg.content}\nCommand Sync Complete!')
        except Exception as e:
            print_stack_trace()
            await ctx.respond(content=str(e), hidden=True)
        print('Done')

    @slash_cog(name='warlord_reboot')
    async def warlord_reboot(self, ctx: SlashedCommand):
        try:
            if ctx.author.id == 198526201374048256:
                confirm = await ask_confirm(self.state, ctx, f'Are you sure you want to reboot Warlord?')
                if confirm:
                    await ctx.respond(content='Rebooting...', hidden=True)
                    import sys
                    sys.exit(1)
                else:
                    await ctx.respond(content='Reboot Canceled!', hidden=True)
        except Exception as e:
            print_stack_trace()
            await ctx.respond(content=str(e), hidden=True)
