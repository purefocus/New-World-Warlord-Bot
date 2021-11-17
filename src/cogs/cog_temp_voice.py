import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import Interaction

from utils.discord_utils import *
import config as cfg

_JOIN_TEMP_GUILD_REF_ = 894675526776676382
_JOIN_TEMP_CHANNEL_REF_ = 910647897433972806

_TEMP_CHANNEL_KEY = '▪'


class TempVoiceChannel:

    def __init__(self, owner: discord.Member, channel: discord.VoiceChannel):
        self.channel = channel
        self.owner = owner

    def matches(self, channel):
        pass


class TempVoiceCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

        self.temporary_channels = {}

    # def save_channels(self):

    async def _create_temp_channel(self, guild: discord.Guild, owner: discord.Member, category) -> discord.VoiceChannel:
        # category = None
        # for cat in guild.categories:
        #     if cat.id == category_id:
        #         category = cat

        overwrites = {
            # guild.default_role: discord.PermissionOverwrite(),
            owner: discord.PermissionOverwrite(mute_members=True, view_channel=True, connect=True, speak=True),
        }
        channel_name = f'{_TEMP_CHANNEL_KEY} {owner.display_name}\'s Channel'
        channel = await guild.create_voice_channel(channel_name, category=category, overwrites=overwrites,
                                                   user_limit=99)

        self.temporary_channels[channel.id] = TempVoiceChannel(owner, channel)
        return channel

    def _is_join_temp_channel(self, state: discord.VoiceState):
        if state.channel is None:
            return False
        return state.channel.guild.id == _JOIN_TEMP_GUILD_REF_ and state.channel.id == _JOIN_TEMP_CHANNEL_REF_

    def _is_temp_channel(self, state: discord.VoiceState):
        if state.channel is None:
            return False
        print(self.temporary_channels)
        return state.channel.id in self.temporary_channels

    async def _identify_temp_channels(self, guild: discord.Guild):
        for vc in guild.voice_channels:
            cname = vc.name
            temp_channel = False
            if ' ' in cname:
                cname = cname.split(' ')[0]

            if _TEMP_CHANNEL_KEY in cname:
                owperms = vc.overwrites
                for key in owperms:
                    if isinstance(key, discord.Member):
                        print(f'Temp channel found! Owner: {key.display_name}')
                        temp_channel = True
                        self.temporary_channels[vc.id] = TempVoiceChannel(key, vc)
                        break

            if temp_channel:
                await self._update_temp_channel(vc)

    async def _remove_temp_channel(self, vc: discord.VoiceChannel):
        if vc.id in self.temporary_channels:
            del self.temporary_channels[vc.id]
        await vc.delete(reason='No users in Temp Channel')

    async def _update_temp_channel(self, vc: discord.VoiceChannel):
        print(vc.members)
        if len(vc.members) == 0:
            await self._remove_temp_channel(vc)

    @commands.Cog.listener()
    async def on_group_join(self, channel: discord.GroupChannel, user: discord.User):
        print(f'{user} has joined {channel.name}')

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        if member.guild.id != _JOIN_TEMP_GUILD_REF_:
            return
        ch1 = before.channel
        ch2 = after.channel
        if self._is_join_temp_channel(after) and ch1 != ch2:
            channel = await self._create_temp_channel(member.guild, member, ch2.category)
            await member.edit(voice_channel=channel)

        if self._is_temp_channel(before) and ch1 != ch2:
            await self._update_temp_channel(ch1)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            if guild.id == _JOIN_TEMP_GUILD_REF_:
                await self._identify_temp_channels(guild)
