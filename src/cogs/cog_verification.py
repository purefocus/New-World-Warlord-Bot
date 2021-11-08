from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
import discord
from utils.botutil import *

from bot_state import *
from utils.details import *

from utils.colorprint import *

from utils.discord_utils import *

import config as cfg


class VerificationCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.channel_name = self.state.config.verify_channel
        self.mod_channel = None
        self.verify_channel = None
        self.vrole = None

    def _has_attachment(self, msg: discord.Message):
        return len(msg.attachments) > 0 or 'https://' in msg.content

    def _get_mod_channel(self, guild: discord.Guild) -> discord.TextChannel:
        if self.mod_channel is None:
            for ch in guild.text_channels:
                if ch.name == self.state.config.mod_verify_channel:
                    self.mod_channel = ch
                    break

        return self.mod_channel

    def _get_verify_channel(self, guild: discord.Guild) -> discord.TextChannel:
        if self.verify_channel is None:
            for ch in guild.text_channels:
                if ch.name == self.state.config.verify_channel:
                    self.verify_channel = ch
                    break

        return self.verify_channel

    def _create_btn(self, label, function, data, color='blurple'):
        return Button(custom_id=f'btn:verify:{function}:{data}', label=label, color=color)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.channel.type != discord.ChannelType.text:
            return

        if msg.channel.name != self.channel_name:
            return

        if msg.author.id == self.client.user.id:
            return

        # if has_role(msg.author, 'Verified'):
        #     return

        # if not self._has_attachment(msg):
        #     return

        keys = ['username', 'company', 'company rank', 'links']
        data = {
            'company': '---',
            'company rank': '---',
            'links': None
        }
        lines = msg.content.split('\n')
        original_text = ''
        for line in lines:
            if 'https://' in line:
                data['links'] = line
                continue
            if ':' in line:
                args = line.split(':', maxsplit=1)
                key, value = args[0].lower().strip(), args[1].strip()
                if key.lower() in keys:
                    data[key.lower()] = value
                    continue
            original_text += f'> {line}'

        if len(data) == len(keys):
            channel = self._get_mod_channel(msg.guild)
            ref = f"{msg.author.id}:{msg.id}"
            control = [
                self._create_btn('Approve', 'yes', ref, 'green'),
                self._create_btn('Deny', 'no', ref, 'red'),
                self._create_btn('Manual', 'edit', ref, 'red')
            ]

            links = data['links'] or ''

            if len(msg.attachments) > 0:
                links = msg.attachments[0].url

            # print(msg.attachments)
            msg_link = f'https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}'
            await channel.send(
                content=f"{msg.author.mention}\n\n"
                        f"> *Name*: **{data['username']}**\n"
                        f"> *Company*: **{data['company']}**\n"
                        f"> *Company Rank*: **{data['company rank']}**\n"
                        f"{links}\n"
                        f"{original_text}"
                        f"\n*Message Reference:* {msg_link}",
                components=control
            )  # ':green_circle'

            await msg.add_reaction(emoji='🟢')

            print_dict(data)
        else:
            await msg.add_reaction(emoji='❌')
            await msg.reply(content='__Please use the following template:__ \n'
                                    '> Username: \n'
                                    '> Company: \n'
                                    '> Company Rank:\n'
                                    '\n'
                                    '*Your username and company must match Exactly as it shows on your bio page to get approval.*',
                            hidden=True)

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):

        data = ctx.data
        if 'custom_id' not in data:
            return
        id: str = data['custom_id']
        if id.startswith('btn:verify:'):  # 11
            btn_args = id.split(':')
            func = btn_args[2]
            author_id = btn_args[3]
            msg_id = btn_args[4]

            vchannel = self._get_verify_channel(ctx.guild)
            nickname = None
            lines = ctx.message.content.split('\n')
            for line in lines:
                if ':' in line:
                    args = line.split(':')
                    key, value = args[0], args[1]
                    if 'Name' in key:
                        nickname = value.strip()

            await ctx.respond(ninja_mode=True)
            user = await ctx.guild.fetch_member(int(author_id))
            if user is None:
                await ctx.respond('Something went wrong! user wasn\'t found!')

            msg = await vchannel.fetch_message(int(msg_id))
            if msg is not None:
                if func == 'no':
                    await msg.add_reaction(emoji='❌')

                if func == 'yes':
                    if self.vrole is None:
                        self.vrole = discord.utils.get(ctx.guild.roles, name="Test1")
                    await user.edit(nick=nickname)
                    await user.add_roles(self.vrole, reason='Verification')
                    await msg.add_reaction(emoji='✅')
                    await ctx.message.edit(
                        content=ctx.message.content + '\n**Verified - Only verified role was added**', components=None)

                if func == 'edit':
                    if self.vrole is None:
                        self.vrole = discord.utils.get(ctx.guild.roles, name="Test1")
                    # user.edit(nick=)
                    await user.add_roles(self.vrole, reason='Verification')
                    await msg.add_reaction(emoji='✅')
                    await ctx.message.edit(
                        content=ctx.message.content + '\n**Manual Edit - Only verified role was added**',
                        components=None)
