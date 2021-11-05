from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog

from utils.botutil import *

from bot_state import *
from utils.details import get_location

from utils.colorprint import *

from utils.discord_utils import *


class VerificationCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.channel_name = self.state.config.verify_channel
        self.mod_channel = None

    def _has_attachment(self, msg: discord.Message):
        return len(msg.attachments) > 0 or 'https://' in msg.content

    # def _get_mod_channel(self, guild: discord.Guild):



    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.channel.name != self.channel_name:
            return

        # if has_role(msg.author, 'Verified'):
        #     return

        if not self._has_attachment(msg):
            return

        keys = ['username', 'company', 'company rank']
        data = {}
        lines = msg.content.split('\n')
        for line in lines:
            if ':' in line:
                args = line.split(':', maxsplit=1)
                key, value = args[0], args[1]
                if key.lower() in keys:
                    data[key.lower()] = value

        if len(data) == len(keys):
            print_dict(data)
