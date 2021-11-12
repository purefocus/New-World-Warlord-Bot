from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
import discord
from utils.botutil import *

from bot_state import *
from utils.details import *

from utils.colorprint import *

from utils.discord_utils import *

import config as cfg


def _create_btn(label, function, data, color='blurple'):
    return Button(custom_id=f'btn:verify:{function}:{data}', label=label, color=color)


class VerifyRequest:

    def __init__(self, user: discord.Member):
        self.user = user
        self.username = None
        self.company = None
        self.image = None

        self.status = 'Unverified'

    def _check(self, ctx: Interaction):
        return ctx.author == self.user and ctx.channel.type == discord.ChannelType.private

    def _check2(self, ctx: Interaction):
        print(ctx.author)
        return ctx.author == self.user

    async def request_info_from_user(self, client: discord.Client):
        try:
            await self.user.send(
                f'Hello {self.user.mention}!\n'
                f'\n '
                f'You\'ll need to verify your identity before we can give you access to this discord server!\n'
                f'\n'
                f'What in your **in-game username**?'
            )
            response: discord.Message = await client.wait_for('message', check=self._check, timeout=120)
            self.username = response.content

            btns = [
                Button(custom_id='btn:yes', label='Yes', color='green'),
                Button(custom_id='btn:no', label='No', color='red')
            ]
            msg: Message = await self.user.send('Are you in a company?', components=btns)
            btn: PressedButton = await msg.wait_for('button', client=client, check=self._check2, timeout=120)
            print('msg: ', btn)
            if btn.custom_id == 'btn:yes':
                await msg.edit('What **company** are you in? (Please type it exactly like it shows in game)',
                               components=None)
                response: discord.Message = await client.wait_for('message', check=self._check, timeout=120)
                self.company = response.content

            await self.user.send('Please *post* or link* a screenshot of your character **bio page**!')

            attempts = 0
            while True:
                response: discord.Message = await client.wait_for('message', check=self._check, timeout=120)
                link = response.content

                if len(response.attachments) > 0:
                    link = response.attachments[0].url

                if link.startswith('https://') or link.startswith('http://'):
                    break

                attempts += 1
                if attempts > 3:
                    await self.user.send('Please contact a Moderator for assistance!')
                    return False
                else:
                    await self.user.send(
                        'That is an invalid image! Please post or link a screenshot of your character bio page!')

            self.image = link

            embed = discord.Embed(title='Verification Request', colour=discord.Colour.magenta())
            self.add_embed_fields(embed)

            msg: Message = await self.user.send('Is this information correct?', embed=embed, components=btns)
            btn: PressedButton = await msg.wait_for('button', client=client, check=self._check2, timeout=120)

            if btn.custom_id == 'btn:yes':
                await msg.edit(
                    'Your faction verification has been submitted!\n'
                    'You will be notified when a moderator reviews your information!',
                    components=None)
                return True
            else:
                return False
        except Exception as e:
            self.user.send(f'Something went wrong! ({str(e)})\n'
                           'Please try again or contact a Moderator for assistance!', components=[
                Button(custom_id='btn:verification_btn', label='Click here to verify!', color='green')
            ])

    def add_embed_fields(self, embed: discord.Embed):
        embed.add_field(name='User', value=self.user.mention)
        embed.add_field(name='Character Name', value=self.username)
        embed.add_field(name='Company', value=self.company or '\u200b')
        embed.set_image(url=self.image)


class DMVerificationCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state
        self.guild = None
        self.vchannel: discord.TextChannel = None

    @commands.Cog.listener()
    async def on_ready(self):
        self.guild: discord.Guild = self.state.config.faction_guild
        for ch in self.guild.text_channels:
            if ch.name == self.state.config.mod_verify_channel:
                self.vchannel = ch
                break
        # user = await self.guild.fetch_member(198526201374048256)
        # print(user)
        # req = VerifyRequest(user)
        # await req.request_info_from_user(self.client)

    def create_verification_embed(self, req: VerifyRequest):
        embed = discord.Embed(title='Verification Request', colour=discord.Colour.magenta())
        company_role = find_company_role(self.guild, req.company)


        return embed

    async def post_verification(self, req):
        ref = f"{req.user.id}"

        control = []
        control.append(_create_btn('Set Name', 'name', ref, 'green'))
        control.append(_create_btn('Set Company', 'company', ref, 'green'))
        control.append(_create_btn('Verify', 'verify', ref, 'green'))
        control.append(_create_btn('Deny', 'no', ref, 'red'))
        control.append(_create_btn('Done', 'done', ref, 'blurple'))

        embed = self.create_verification_embed(req)

        await self.vchannel.send(content='', embed=embed, components=control)

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):
        data = ctx.data
        if 'custom_id' not in data:
            return
        id: str = data['custom_id']
        if id == 'btn:verification_btn':
            await ctx.respond(ninja_mode=True)
            req = VerifyRequest(ctx.author)
            # await req.request_info_from_user(self.client)
            req.user = self.guild.get_member(198526201374048256)
            req.company = None
            req.image = 'https://cdn.discordapp.com/attachments/897102590536478761/908785314917670962/unknown.png'
            req.username = 'purefocus'
            print('post!')
            await self.post_verification(req)
