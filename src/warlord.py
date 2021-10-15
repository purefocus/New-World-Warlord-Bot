from discord.ext import commands
import discord

from bot_state import *
from forms.create_war import *
from forms.enlist_form import cmd_enlist
from forms.war_management import *
from forms.bot_configure import *
from utils.botutil import *

from utils.colorprint import *


class WarlordBot(commands.Bot):

    def __init__(self, config):
        super().__init__(' ')

        self.config = config

    async def on_ready(self):
        servers = {}
        for guild in self.guilds:
            guild: discord.Guild = guild
            servers[guild.name] = guild.id

        print_dict(servers, f'{colors.blue(self.user)} has logged into')

    async def on_error(self, event_method: str, *args, **kwargs) -> None:
        await super(WarlordBot, self).on_error(event_method, args, kwargs)
        print_dict({
            'event_method': event_method,
            'args': args,
            'kwargs': kwargs
        })


if __name__ == '__main__':
    config = Config()
    config.load()
    bot = WarlordBot(config)
    bot.run(config.bot_token)
