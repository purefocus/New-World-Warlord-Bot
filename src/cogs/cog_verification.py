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

    def _set_embed_status(self, msg: Message, status: str = None, error=None):
        embed = msg.embeds
        if len(embed) > 0:
            embed = embed[0]
        if embed is not None:
            # embed.set_field_at(2, name='Status', value=status)
            if status is not None:
                for field in embed.fields:
                    if field.name == 'Status':
                        field.value = status

            if error is not None:
                has_err_field = False
                for field in embed.fields:
                    if field.name == 'Error':
                        field.value = f'{field.value}\n{error}'
                        has_err_field = True
                        break
                if not has_err_field:
                    embed.add_field(name='Error', value=error)

        return embed

    def _create_verification_embed(self, username, company, link, msg, otext):
        ref = f"{msg.author.id}:{msg.id}"
        control = []
        control.append(self._create_btn('Set Name', 'name', ref, 'green'))
        if company is not None:
            control.append(self._create_btn('Set Company', 'company', ref, 'green'))
        control.append(self._create_btn('Verify', 'verify', ref, 'green'))
        control.append(self._create_btn('Deny', 'no', ref, 'red'))

        msg_link = f'https://discord.com/channels/{msg.guild.id}/{msg.channel.id}/{msg.id}'

        embed = discord.Embed(title='Verification Request',
                              color=discord.Color.dark_magenta(),
                              description=f'[Message Reference]({msg_link})')
        embed.add_field(name='User', value=msg.author.mention)
        embed.add_field(name='Character Name', value=username)
        if company is not None:
            embed.add_field(name='Company', value=company)

        embed.add_field(name='Status', value='Unverified')
        embed.add_field(name='Original Message', value=otext, inline=False)

        matched_names = check_for_matching_name(username, msg.guild)
        if len(matched_names) > 0:
            names = ''
            for user in matched_names:
                names += f"> {user.mention} ({user.joined_at.strftime('%b %d, %I:%M %p %Z')})\n"
            embed.add_field(name='Possible Duplicates!', value=names, inline=False)

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
        company = None
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

            elif company is None and len(line) > 1:
                company = line

            original_text += f'> {line}\n'

        return username, company, link, original_text

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

        username, company, link, otext = self._parse_data(msg)

        if username is not None and link is not None:
            channel = self._get_mod_channel(msg.guild)

            msg_data = self._create_verification_embed(username, company, link, msg, otext)

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

        username, company, link, otext = self._parse_data(msg)

        if username is not None and link is not None:
            channel = self._get_mod_channel(msg.guild)

            msg_data = self._create_verification_embed(username, company, link, msg, otext)

            self.awaiting_verifications[msg.author.mention] = await channel.send(**msg_data)
            await msg.add_reaction(emoji='🟢')

        elif link is not None:
            await msg.add_reaction(emoji='❌')
            await msg.reply(content='__Please use the following template:__ \n'
                                    '> <username> \n'
                                    '> <company> \n'
                                    '> <Attachment/link>\n'
                                    '\n'
                                    '*Your username and company must match __exactly__ as it shows on your bio page to get approval.*'
                                    '*Ignore company if you are not in one*',
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

            if len(ctx.message.embeds) > 0:
                embed: discord.Embed = ctx.message.embeds[0]
                field = embed.fields[1]
                nickname = field.value

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
                    update = self._set_embed_status(post, '❌ Denied')

                    await post.edit(embed=update, components=None)
                    # await post.edit(
                    #     content=post.content + f'\n**Verification Denied!**', components=components
                    # )

                if func == 'name':
                    try:
                        await user.edit(nick=nickname)
                        components[0].disabled = True
                        update = self._set_embed_status(post, 'Renamed')
                    except Exception as e:
                        update = self._set_embed_status(post, error=str(e))

                    await post.edit(embed=update, components=components)
                    # await post.edit(
                    #     content=post.content + f'\n**Nickname was set to {nickname}**', components=components
                    # )

                if func == 'verify':
                    if self.vrole is None:
                        self.vrole = discord.utils.get(ctx.guild.roles, name="Verified")

                    await user.add_roles(self.vrole, reason='Verification')
                    await msg.clear_reactions()
                    await msg.add_reaction(emoji='<:done_stamp:895817107797852190>')

                    update = self._set_embed_status(post, '✅ Verified')

                    await post.edit(embed=update, components=None)

                    if user in self.awaiting_verifications:
                        del self.awaiting_verifications[user.mention]
            else:
                update = self._set_embed_status(post, '❗ Message Not Found!')

                await post.edit(embed=update, components=None)
                # await post.edit(
                #     content=post.content + '\n\n**[Error] Referenced message was unable to be found!.**\n',
                #     components=None)

            if not ctx.responded:
                await ctx.respond(ninja_mode=True)
