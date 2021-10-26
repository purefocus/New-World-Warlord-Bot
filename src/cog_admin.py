import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import SlashOption, SlashPermission, SlashedCommand
from discord_ui import Interaction

from views.view_confirm import ask_confirm

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


async def _make_role(name: str, guild: discord.Guild):
    role = await guild.create_role(name=name,
                                   colour=discord.Colour(0xb9adff),
                                   permissions=discord.Permissions(permissions=2147863617),
                                   hoist=True,
                                   mentionable=False,
                                   reason='Adding a new faction tag')


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
                faction = ' '.join(args[2:])

                guild: discord.Guild = ctx.guild

                # _get_all_faction_roles(guild)
                found = False
                for role in guild.roles:
                    role: discord.Role = role
                    if role.name.lower() == faction.lower():
                        found = True

                if found:
                    await ctx.respond('Role Found!', hidden=True)
                else:
                    await ctx.respond('Role Not Found!', hidden=True)
                    add_role = await ask_confirm(self.state, ctx,
                                                 f'Would you like to add the new faction role **{faction}**?')
                    if add_role:
                        await _make_role(faction, guild)

                    await ctx.send(
                        f'Role {faction} Added!\n *Don\'t forget to change the role\'s position in the server role list!*',
                        hidden=True)
            elif args[0] == 'guide':
                from views.Guide import create_embed
                embed = create_embed()
                await ctx.send(embed=embed)
            elif args[0] == 'tag':
                self.state.config.tag_war = args[1] == 'en'


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
            await ctx.respond(content=str(e), hidden=True)
        print('Done')
