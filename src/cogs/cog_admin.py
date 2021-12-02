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

admin_cmd_cfg = {
    'guild_ids': [894675526776676382],
    'guild_permissions': {
        894675526776676382: SlashPermission(
            allowed={
                '894677353479942154': SlashPermission.Role,  # Admin
                '895490018246815776': SlashPermission.Role,  # Moderator
                '198526201374048256': SlashPermission.User  # purefocus
            }
        )
    }
}


def _get_all_faction_roles(guild: discord.Guild):
    factions = []
    non_factions = []
    for role in guild.roles:
        if role.colour.value == 0xb9adff:
            factions.append(role.name)
        else:
            non_factions.append(role.name)

    print('Factions: ', factions)
    print('Non Factions: ', non_factions)


async def _make_company_role(name: str, guild: discord.Guild):
    role = await guild.create_role(name=name,
                                   colour=discord.Colour(0xb9adff),
                                   permissions=discord.Permissions(permissions=2147863617),
                                   hoist=True,
                                   mentionable=False,
                                   reason='Adding a new company tag')
    return role


class AdminCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState, ui: discord_ui.UI):
        self.client = client
        self.state = state
        self.ui = ui

        # guild.create_role(name=faction)

    # @slash_cog(name='admin', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    # async def cmd_admin(self, ctx: SlashedCommand):
    #     await ctx.send('base command!')

    @subslash_cog(base_names=['admin', 'company'], name='create', options=[
        SlashOption(str, name='Name', description='Name of the company you wish to create', required=True)
    ], **admin_cmd_cfg)
    async def cmd_admin_company(self, ctx: SlashedCommand, name: str):
        guild: discord.Guild = ctx.guild

        # _get_all_faction_roles(guild)
        found = False
        for role in guild.roles:
            role: discord.Role = role
            if role.name.lower() == name.lower():
                found = True

        if found:
            await ctx.respond('The role already exists!', hidden=True)
        else:
            add_role, msg = await ask_confirm(self.state, ctx,
                                              f'Would you like to add the new faction role **{name}**?', ret_msg=True)
            if add_role:
                await _make_company_role(name, guild)

            await msg.edit(
                f'Role {name} Added!\n *Don\'t forget to change the role\'s position in the server role list!*',
                components=None)
