from discord.ext import commands, tasks
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
import discord
from utils.data import MessageReference
from bot_state import BotState

from utils.world_status import get_status


class WorldStatusCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.update_status.start()

    @tasks.loop(minutes=5)
    async def update_status(self):

        status = self.state.world_status = get_status(self.state.config.nws_token)
        await self.state.update_presence(str(status))

        msgs = self.state.config.get_messages('world-status')
        if msgs is not None:
            for msg in msgs:
                msg: MessageReference = msg

                embed = discord.Embed(title='Ohonoo World Status', colour=discord.Color.purple())
                embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W_400x400.jpg')
                embed.set_image(
                    url='https://images.ctfassets.net/j95d1p8hsuun/29peK2k7Ic6FsPAVjHWs8W/06d3add40b23b20bbff215f6979267e8/NW_OPENGRAPH_1200x630.jpg')
                embed.add_field(name='Player Count', value=f'{status.players_current}/{status.players_maximum}')
                if status.queue_wait_time_minutes > 0:
                    embed.add_field(name='Queue Size',
                                    value=f'{status.queue_current} ({status.queue_wait_time_minutes} mins)')
                else:
                    embed.add_field(name='Queue Size', value=f'{status.queue_current}')

                embed.add_field(name='Status', value=f'{status.status_enum}')

                embed.set_footer(text=f'Last Updated • {status.last_updated}')

                m = await msg.get_message(self.client)
                await m.edit(content=' ', embed=embed)

    @update_status.before_loop
    async def before_update_status(self):
        await self.client.wait_until_ready()
        status = self.state.world_status = get_status(self.state.config.nws_token)
        await self.state.update_presence(str(status))
