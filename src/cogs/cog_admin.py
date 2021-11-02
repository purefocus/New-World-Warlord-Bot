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

admin_permissions = SlashPermission(
    allowed={
        '894677353479942154': SlashPermission.Role,  # Admin
        '895490018246815776': SlashPermission.Role,  # Moderator
        '198526201374048256': SlashPermission.User  # purefocus
    }
)
guild_permissions = {
    '894675526776676382': admin_permissions
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

    @slash_cog(name='test_cmd', options=[
        SlashOption(str, 'arguments', 'command args', required=True)
    ], guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    async def test_cmd(self, ctx: discord_ui.SlashedCommand, arguments: str):
        args = arguments.split(' ')
        try:
            if len(args) == 0:
                await ctx.respond('test!', hidden=True)
            elif args[0] == 'new' and args[1] == 'faction':
                await ctx.respond('Changed to `/admin company create <company name>`', hidden=True)

            elif args[0] == 'guide':
                from views.Guide import create_embed
                embed = create_embed()
                await ctx.send(embed=embed)

            elif args[0] == 'tag':
                self.state.config.tag_war = args[1] == 'en'

            elif args[0] == 'weap':
                selected = await ask_weapon_mastery(self.state, ctx)
                print('Selected: ', selected)


        except Exception as e:
            await ctx.send(str(e), hidden=True)

        # guild.create_role(name=faction)

    @slash_cog(name='warlord_cmd_sync', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    async def warlord_cmd_sync(self, ctx: SlashedCommand):
        try:
            await ctx.defer(hidden=True)
            await self.ui.slash.sync_commands(delete_unused=False)
            await ctx.respond('Done!', hidden=True)
        except Exception as e:
            print_stack_trace()
            await ctx.respond(content=str(e), hidden=True)
        print('Done')

    @slash_cog(name='warlord_reboot', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    async def warlord_reboot(self, ctx: SlashedCommand):
        # if ctx.author.name == 'purefocus':
        confirm = await ask_confirm(self.state, ctx, f'Are you sure you want to reboot Warlord?')
        if confirm:
            await ctx.respond(content='Rebooting...', hidden=True)
            import sys
            sys.exit(1)
        else:
            await ctx.respond(content='Reboot Canceled!', hidden=True)

    # @slash_cog(name='admin', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    # async def cmd_admin(self, ctx: SlashedCommand):
    #     await ctx.send('base command!')

    @subslash_cog(base_names=['admin', 'company'], name='create', options=[
        SlashOption(str, name='Name', description='Name of the company you wish to create', required=True)
    ], guild_ids=[894675526776676382], guild_permissions=guild_permissions)
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
                f'Role {name} Added!\n *Don\'t forget to change the role\'s position in the server role list!*')
