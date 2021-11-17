import discord
import asyncio
from discord_ui import *
from bot_state import BotState
from config import *
from utils.permissions import *
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
import discord
from utils.botutil import *
import discord_ui
import config as cfg

from utils.colorprint import *
import pickle


class WarVoiceChannelSetup:

    def __init__(self, war, manager: discord.Member):
        super().__init__()
        self.guild = None
        self.war: WarDef = war
        self.category = None
        self.manager = manager
        self.invite_code = {}
        self.channels = {}
        self.manage_msg = None

    async def management_message(self):
        embed = self.create_management_embed()
        components = self.create_controls()
        if self.manage_msg is None:
            self.manage_msg = await self.manager.send('War Management!', embed=embed, components=components)
        else:
            self.manage_msg = await self.manage_msg.edit('War Management!', embed=embed, components=components)

    def create_controls(self):
        return None

    def create_management_embed(self):
        embed = discord.Embed(title=f'War Voice Channel Management')
        if self.invite_code is not None:
            embed.add_field(name='Direct Invite Code', value=self.invite_code)

        if len(self.channels) == 0:
            embed.add_field(name='Channels', value='Channels not configured yet!', inline=False)
        else:
            value = ''
            for ch in self.channels:
                value += f'> {ch}'
        return embed

    async def push_updates(self, guild: discord.Guild):
        if self.category is None:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                self.manager: discord.PermissionOverwrite(mute_members=True, view_channel=True, connect=True,
                                                          speak=True, move_members=True),
            }
            self.category = await guild.create_category(self.war.location, overwrites=overwrites)
        for ch in self.channels:
            channel = self.channels[ch]
            if self.invite_code is None:
                if channel is None:
                    channel = await self.category.create_voice_channel(ch)
                    self.channels[ch] = channel
                    self.invite_code = channel.create_invite(temporary=False, max_age=60 * 60)


class WarVoiceCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.active_setups = {}
        self.load()

    def save(self):
        try:
            pickle.dump(self.active_setups, open(cfg.tmpfile('war_voice.pickle'), 'wb'))
        except Exception as e:
            print(str(e))

    def load(self):
        try:
            self.active_setups = pickle.load(open(cfg.tmpfile('war_voice.pickle'), 'rb'))
        except Exception as e:
            print(str(e))
            self.active_setups = {}

    @subslash_cog(base_names=['war', 'voice'], name='setup')
    async def cmd_war_voice(self, ctx: Interaction):
        if not await check_permission(ctx, Perm.WAR_HOST):
            return
        war, _ = await select_war(self.state, ctx, 'Select the war to get the enlistment roster for',
                                  allow_multiple=False,
                                  allow_overall=False)

        if war is not None:
            setup: WarVoiceChannelSetup = self.active_setups[war.id]
            if setup is not None:
                await ctx.respond(
                    f'This war voice is already being managed by {setup.manager}! '
                    f'You\'ll need to talk to them to get management permissions. '
                    f'If this is a mistake, please contact a Moderator!',
                    hidden=True)
                return
            setup = self.active_setups[war.id] = WarVoiceChannelSetup(war, ctx.author)
            await setup.management_message()

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):
        if ctx.type == discord_ui.InteractionType.Component:
            custom_id = str(ctx.data['custom_id'])
            if custom_id.startswith('btn:warvoice:'):
                custom_id = custom_id.split(':')
