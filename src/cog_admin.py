import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import SlashOption, SlashPermission, SlashedCommand
from discord_ui import Interaction

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


class AdminCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState, ui: discord_ui.UI):
        self.client = client
        self.state = state
        self.ui = ui

    @slash_cog(name='new_faction', options=[
        SlashOption(str, 'faction', 'The name of the faction', required=True)
    ], guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    async def new_faction(self, ctx: discord_ui.SlashedCommand, faction: str):

        guild: discord.Guild = ctx.guild

        for role in guild.roles:
            role: discord.Role = role
            if role.name.lower() == faction.lower():
                await ctx.respond('Role Found!')
            else:
                await ctx.respond('Role Not Found!')

        # guild.create_role(name=faction)

    @slash_cog(name='warlord_cmd_sync', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    async def warlord_cmd_sync(self, ctx: SlashedCommand):
        try:
            await ctx.defer(hidden=True)
            await self.ui.slash.sync_commands(delete_unused=True)
            await ctx.respond('Done!', hidden=True)
        except Exception as e:
            await ctx.respond(content=str(e), hidden=True)
        print('Done')
