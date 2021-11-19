from discord.ext import commands, tasks
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
import discord
from utils.data import MessageReference
from bot_state import BotState

from utils.world_status import get_status, WorldStatus

from utils.botutil import *


class WorldStatusCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.update_status.start()

        # self.status_channels = {
        #     897098434153185290: {
        #         'players_online': 911268108973518848,
        #         'queue_size': 911268109900480572,
        #         'status': 911268110428934254,
        #     }
        # }

    def create_status_embed(self, status: WorldStatus) -> discord.Embed:

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

        embed.set_footer(text=f'⌚ Last Updated • {status.last_updated}')

        return embed

    async def update_status_messages(self, status: WorldStatus):

        # status = self.state.world_status = get_status(self.state.config.nws_token)
        await self.state.update_presence(str(status))

        msgs = self.state.config.get_messages('world-status')
        if msgs is not None:
            embed = self.create_status_embed(status)
            for msg in msgs:
                msg: MessageReference = msg

                m = await msg.get_message(self.client)
                await m.edit(content=' ', embed=embed)

    async def create_status_channels(self, guild: discord.Guild):
        try:
            # cat_id = 911261832881250314
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(mute_members=False, view_channel=True, connect=False,
                                                                speak=False),
            }
            cat = await guild.create_category(name='Server Status',
                                              overwrites=overwrites,
                                              reason='Creating Server Status',
                                              position=0)

            # await cat.create_voice_channel(name='Server: Ohonoo')
            status = await cat.create_voice_channel(name='Ohonoo: xxxx')
            players_online = await cat.create_voice_channel(name='Online: xxxx')
            queue_size = await cat.create_voice_channel(name='Queue: xxxx')

            self.state.config.status_channels[guild.id] = {
                'status': status.id,
                'players_online': players_online.id,
                'queue_size': queue_size.id,
            }
            self.state.config.save()

            status = self.state.world_status = get_status(self.state.config.nws_token)
            await self.update_status_channels(status)
        except Exception as e:
            print_stack_trace()

    async def update_status_channels(self, status: WorldStatus):
        for gid in self.state.config.status_channels:
            try:
                channels = self.state.config.status_channels[gid]
                guild = self.client.get_guild(int(gid))

                ch = guild.get_channel(channels['players_online'])
                await ch.edit(name=f'Online: {status.players_current}/{status.players_maximum}')

                ch = guild.get_channel(channels['queue_size'])
                await ch.edit(name=f'Queue: {status.queue_current}')

                ch = guild.get_channel(channels['status'])
                await ch.edit(name=f'Ohonoo : {status.status_enum}')

            except Exception as e:
                print_stack_trace()

    @tasks.loop(minutes=5)
    async def update_status(self):
        status = self.state.world_status = get_status(self.state.config.nws_token)
        await self.state.update_presence(str(status))
        await self.update_status_messages(status)
        await self.update_status_channels(status)

    @update_status.before_loop
    async def before_update_status(self):
        await self.client.wait_until_ready()
        status = self.state.world_status = get_status(self.state.config.nws_token)
        await self.state.update_presence(str(status))
        await self.update_status_messages(status)
        await self.update_status_channels(status)

    # @commands.Cog.listener()
    # async def on_ready(self):
    #
    #     guild = self.client.get_guild(897098434153185290)
    #     has_cat = False
    #     for cat in guild.categories:
    #         if cat.name == 'Server Status':
    #             for ch in cat.channels:
    #                 await ch.delete()
    #             await cat.delete()
    #             return
