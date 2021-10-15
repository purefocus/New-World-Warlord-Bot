from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog

from bot_state import *


class CogConfig(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='warlord_config')
    async def warlord_config(self, ctx, *args):
        pass

    @warlord_config.command(name='channel')
    async def warlord_config2(self, ctx, *args):
        pass
