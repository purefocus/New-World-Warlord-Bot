import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import Interaction


async def question(ctx, question):
    pass


class FactionsCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='clear_messages')
    async def command(self, ctx: discord_ui.SlashedCommand):
        if ctx.author.name == 'purefocus#3061':
            await ctx.respond(content='Permissions Approved!', hidden=True)
        else:
            await ctx.respond(content='Not Yet Implemented', hidden=True)
