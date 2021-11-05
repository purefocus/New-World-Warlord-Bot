import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import Interaction

from utils.discord_utils import *


class ExtrasCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='channel_stats', guild_ids=[894675526776676382])
    async def cmd_war_stats(self, ctx: discord_ui.SlashedCommand):
        user: discord.Member = ctx.author

        if user.voice is None:
            await ctx.respond('You must be in a voice channel to use this command!', hidden=True)
            return

        channel = user.voice.channel
        data = {'No Company': []}
        members = channel.members
        for user in members:
            company = get_company_role(user)
            if company is None:
                data['No Company'].append(user)
            else:
                if company not in data:
                    data[company] = []
                data[company].append(user.display_name)

        embed = discord.Embed(title='Channel Stats')
        embed.add_field(name='Participants', value=str(len(members)), inline=False)

        for comp in data:
            users = data[comp]
            if len(users) > 0:
                value = ''
                for user in users:
                    value += f'{user}\n'
                embed.add_field(name=f'{comp} ({len(users)})', value=value)
        embed.set_footer(text='Generated using /channel_stats')

        await ctx.respond(embed=embed, hidden=True)
