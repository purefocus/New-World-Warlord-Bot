import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import Interaction


class ExtrasCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='/whelp')
    async def cmd_help(self, ctx: discord_ui.SlashedCommand):
        from views.Guide import create_embed
        embed = create_embed()
        await ctx.send(embed=embed)
