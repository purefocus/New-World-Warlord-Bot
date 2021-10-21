import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui.slash import SlashOption, SlashPermission
from discord_ui import Interaction


class AdminCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='new_faction', options=[
        SlashOption(str, 'faction', 'The name of the faction', required=True)
    ], guild_ids=[894675526776676382], guild_permissions=SlashPermission(
        allowed={
            '894677353479942154': SlashPermission.ROLE,  # Admin
            '895490018246815776': SlashPermission.ROLE,  # Moderator
            '198526201374048256': SlashPermission.USER  # purefocus
        }))
    async def command(self, ctx: discord_ui.SlashedCommand, faction: str):

        guild: discord.Guild = ctx.guild

        for role in guild.roles:
            role: discord.Role = role
            if role.name.lower() == faction.lower():
                await ctx.respond('Role Found!')
            else:
                await ctx.respond('Role Not Found!')

        # guild.create_role(name=faction)
