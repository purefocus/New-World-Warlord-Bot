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

        if has_role(msg.author, 'Verified'):
            return

        # if not self._has_attachment(msg):
        #     return

        keys = ['username', 'links']
        data = {}
        if len(msg.attachments) > 0:
            data['links'] = msg.attachments[0].url
        lines = msg.content.split('\n')
        original_text = ''
        username = None
        for line in lines:
            if username is None and len(line) > 0:
                username = line
                data['username'] = username
            if 'https://' in line:
                data['links'] = line
                continue
            original_text += f'> {line}'

        if len(data) == len(keys):
            channel = self._get_mod_channel(msg.guild)
            ref = f"{msg.author.id}:{msg.id}"
            control = [
                self._create_btn('Set Name', 'name', ref, 'green'),
                self._create_btn('Verify', 'verify', ref, 'green'),
                self._create_btn('Deny', 'no', ref, 'red'),
            ]

            links = data['links'] or ''

            # print(msg.attachments)
            msg_link = f'https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}'
            await channel.send(
                content=f"{msg.author.mention}\n\n"
                        f"> *Name*: **{data['username']}**\n\n"
                        f"{links}\n"
                # f"{original_text}"
                        f"\n\n*Message Reference:* {msg_link}",
                components=control
            )  # ':green_circle'

            await msg.add_reaction(emoji='🟢')

            print_dict(data)
        else:
            await msg.add_reaction(emoji='❌')
            await msg.reply(content='__Please use the following template:__ \n'
                                    '> <username> \n'
                                    '> <Attachment/link>\n'
                                    '\n'
                                    '*Your username must match __exactly__ as it shows on your bio page to get approval.*',
                            )

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
                        value = value.replace('*', '')
                        nickname = value.strip()

            user = await ctx.guild.fetch_member(int(author_id))
            if user is None:
                await ctx.respond('Something went wrong! user wasn\'t found!')

            msg = await vchannel.fetch_message(int(msg_id))
            if msg is not None:
                if func == 'no':
                    await msg.add_reaction(emoji='❌')
                    await ctx.message.edit(
                        content=ctx.message.content + f'\n**Verification Denied!**', components=None)

                if func == 'name':
                    await user.edit(nick=nickname)

                    await ctx.message.edit(
                        content=ctx.message.content + f'\n**Nickname was set to {nickname}**', components=None)

                if func == 'verify':
                    if self.vrole is None:
                        self.vrole = discord.utils.get(ctx.guild.roles, name="Test1")
                    await user.add_roles(self.vrole, reason='Verification')
                    await msg.add_reaction(emoji='✅')
                    await ctx.message.edit(
                        content=ctx.message.content + '\n**Verified role was added and post was marked done.**',
                        components=None)

            if not ctx.responded:
                await ctx.respond(ninja_mode=True)
