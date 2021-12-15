import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

from utils.botutil import *
from utils.pdfgen import *
from bot_state import BotState
from views.roster import create_roster_embed
import discord_ui
from discord_ui import SlashOption, SlashPermission, SlashedCommand
from discord_ui import Interaction
from views.weapon_selection import ask_weapon_mastery
from views.view_confirm import ask_confirm

from utils.botutil import print_stack_trace
from utils.discord_utils import *
import pandas as pd
import os
from utils.colorprint import *

import config as cfg
import time
from utils.permissions import *

last_message_time = 0


class WarGroupsCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='parse_groups',
               description='Reposts the war notification',
               options=[
                   SlashOption(str, name='id', description='The id link to a google sheet with permission to view.',
                               required=True),
                   SlashOption(str, name='sheet', description='The name of the sheet that the group information is on.',
                               required=True)
               ])
    async def parse_groups(self, ctx, id, sheet):
        print('parse groups command')
        if not await check_permission(ctx, Perm.WAR_ROSTER):
            return

        link = f'https://docs.google.com/spreadsheets/d/{id}'
        embed = await self.parse_and_post(ctx, link, sheet)
        if embed is not None:
            await ctx.respond(embed=embed)
        else:
            await ctx.respond('Unable to process the sheet provided!')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if self.client.user.mentioned_in(msg):
            try:
                if msg.author == self.client.user:
                    return
                if '[roster]' not in msg.content.lower():
                    return
                try:
                    lines = msg.content.split('\n')
                    url = lines[2]
                    sheet = lines[3]
                    cid = -1
                    if len(lines) == 5:
                        channel_tag = lines[4].strip()
                        if channel_tag.startswith('<#') and channel_tag.endswith('>'):
                            channel_tag = channel_tag[2:-1]
                            cid = int(channel_tag)

                    dir_split = url.split('/')
                    if 'edit' in dir_split[-1]:
                        url = url.replace('/' + dir_split[-1], '')
                    print('Sheet URL: ', url)
                    embed = self.get_group_embed(url, sheet)

                    try:
                        if cid != -1:
                            channel = msg.guild.get_channel(cid)
                            await channel.send(embed=embed)
                            return
                    except:
                        print_stack_trace()
                    await msg.reply(embed=embed)


                except:
                    print_stack_trace()
                    await msg.reply('Unable to process the message!\n'
                                    'Please use the following template:\n'
                                    '```@Warlord\n'
                                    '[roster]\n'
                                    '<google sheet url>\n'
                                    '<sheet name>```')

            except:
                print_stack_trace()

    def get_group_embed(self, link, sheet):

        from utils.google_forms import pull_from_sheet
        from utils.details import role_emoji
        groups, details = pull_from_sheet(link, sheet.replace(' ', '+'))

        val = ''
        for key in details:
            value = details[key]
            val += f'**{key}**: {value}\n'
        # if len(val) > 0:
        #     embed.add_field(name='Details', value=val, inline=False)

        embed = discord.Embed(title='Group Assignments', description=val)
        for group, members in groups:
            value = ''
            for member, role in members:
                if role is None:
                    role = ''
                if member is None:
                    member = ''
                value += f'{role_emoji(role)} {member}\n'
            embed.add_field(name=group, value=value)

        return embed
