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

        self.awaiting_verifications = {}

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

    def _set_embed_status(self, msg: Message, status: str):
        embed = msg.embed
        if embed is not None:
            embed.set_field_at(2, name='Status', value=status)

        return embed

    def _create_verification_embed(self, username, link, msg, status):
        ref = f"{msg.author.id}:{msg.id}"

        control = [
            self._create_btn('Set Name', 'name', ref, 'green'),
            self._create_btn('Verify', 'verify', ref, 'green'),
            self._create_btn('Deny', 'no', ref, 'red'),
        ]

        msg_link = f'https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}'

        embed = discord.Embed(title='Verification Request', color=discord.Color.dark_magenta(),
                              description=f'[Message Reference]({msg_link})')
        embed.add_field(name='User', value=msg.author.mention)
        embed.add_field(name='Character Name', value=username)
        embed.set_image(url=link)
        embed.set_footer(text=time.strftime('%b %d, %I:%M %p %Z'))
        return {
            'content': '',
            'embed': embed,
            'components': control
        }

    def _parse_data(self, msg: discord.Message):
        link = None
        username = None
        if len(msg.attachments) > 0:
            link = msg.attachments[0].url

        lines = msg.content.split('\n')
        original_text = ''
        for line in lines:
            if 'https://' in line:
                link = line
                continue

            elif username is None and len(line) > 0:
                username = line

            original_text += f'> {line}'

        return username, link, original_text

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, msg: discord.Message):
        if msg.channel.type != discord.ChannelType.text:
            return

        if msg.channel.name != self.channel_name:
            return

        if msg.author.id == self.client.user.id:
            return

        if has_role(msg.author, 'Verified'):
            return

        username, link, otext = self._parse_data(msg)

        if username is not None and link is not None:
            channel = self._get_mod_channel(msg.guild)

            msg_data = self._create_verification_embed(username, link, msg)

            edited = False
            sent = None
            if msg.author.mention in self.awaiting_verifications:
                m = self.awaiting_verifications[msg.author.mention]
                if m is not None:
                    edited = True
                    sent = await m.edit(**msg_data)
            if not edited:
                sent = await channel.send(**msg_data)

            self.awaiting_verifications[msg.author.mention] = sent

            await msg.clear_reactions()
            await msg.add_reaction(emoji='🟢')

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

        username, link, otext = self._parse_data(msg)

        if username is not None and link is not None:
            channel = self._get_mod_channel(msg.guild)

            msg_data = self._create_verification_embed(username, link, msg)

            msg = await channel.send(**msg_data)
            self.awaiting_verifications[msg.author.mention] = msg
            await msg.add_reaction(emoji='🟢')

        elif link is not None:
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
            try:
                msg = await vchannel.fetch_message(int(msg_id))
            except:
                msg = None

            post: Message = ctx.message
            if msg is not None:
                components = post.components
                if func == 'no':
                    await msg.add_reaction(emoji='❌')
                    await post.edit(
                        content=post.content + f'\n**Verification Denied!**', components=None
                    )

                if func == 'name':
                    await user.edit(nick=nickname)
                    components[0].disabled = True
                    update = self._set_embed_status(post, 'Name Set')

                    await post.edit(embed=update, components=None)
                    # await post.edit(
                    #     content=post.content + f'\n**Nickname was set to {nickname}**', components=components
                    # )

                if func == 'verify':
                    if self.vrole is None:
                        self.vrole = discord.utils.get(ctx.guild.roles, name="Verified")

                    await user.add_roles(self.vrole, reason='Verification')
                    await msg.clear_reactions()
                    await msg.add_reaction(emoji='<:done_stamp:895817107797852190>')

                    update = self._set_embed_status(post, 'Verified')

                    await post.edit(embed=update, components=None)

                    if user in self.awaiting_verifications:
                        print('User Verified')
                        del self.awaiting_verifications[user.mention]
            else:
                await post.edit(
                    content=post.content + '\n\n**[Error] Referenced message was unable to be found!.**\n',
                    components=None)

            if not ctx.responded:
                await ctx.respond(ninja_mode=True)
