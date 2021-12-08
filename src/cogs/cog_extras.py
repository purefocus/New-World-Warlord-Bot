import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import Interaction
from utils.permissions import *

from utils.discord_utils import *
import config as cfg


class ExtrasCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @slash_cog(name='channel_stats', **cfg.cmd_cfg)
    async def cmd_war_stats(self, ctx: discord_ui.SlashedCommand):
        user: discord.Member = ctx.author

        if user.voice is None:
            await ctx.respond('You must be in a voice channel to use this command!', hidden=True)
            return

        channel = user.voice.channel
        data = {'No Company': []}
        members = channel.members
        for user in members:
            u = self.state.users[user]
            name = user.display_name
            company = get_company_role(user)
            if company is None and u is not None:
                company = u.company
                name = u.username

            if company is None:
                data['No Company'].append(name)
            else:
                if company not in data:
                    data[company] = []
                data[company].append(name)

        embed = discord.Embed(title='Channel Stats')
        embed.add_field(name='Participants', value=str(len(members)), inline=False)

        for comp in data:
            users = data[comp]
            if len(users) > 0:
                value = ''
                for user in users:
                    value += f'{user}\n'
                embed.add_field(name=f'{comp} ({len(users)})', value=value)
        embed.set_footer(text='Generated using /channel_stats')

        await ctx.respond(embed=embed, hidden=True)

    @slash_cog(name='test_cmd', **cfg.cmd_cfg)
    async def test_cmd(self, ctx: discord_ui.SlashedCommand, arguments: str = None):
        if not await check_permission(ctx, Perm.WAR_POST):
            return
        args = arguments.split(' ')
        cmd = args[0]
        try:
            if cmd == 'check_dupe':
                await self._check_dupe(ctx)

            elif cmd == 'push_roster':
                await self._push_roster(ctx)
        except:
            pass

    @slash_cog(name='wl_test_cmd')
    async def wl_test_cmd(self, ctx: discord_ui.SlashedCommand, cmd: str, param1: str = None, param2: str = None,
                          param3: str = None, param4: str = None):
        if not await check_permission(ctx, Perm.WAR_POST):
            return

        if cmd == 'test':
            await ctx.respond('Test Command!', hidden=True)

        elif cmd == 'check_dupe':
            await self._check_dupe(ctx)

        elif cmd == 'push_roster':
            await self._push_roster(ctx)



        else:
            await ctx.respond('Invalid Test Command', hidden=True)

        if not ctx.responded:
            await ctx.respond('Done.', hidden=True)

    async def _check_dupe(self, ctx: discord_ui.SlashedCommand):
        from utils.discord_utils import search_for_duplicate_names
        result = 'Checkign for duplicated names...\n'
        matches = search_for_duplicate_names(ctx.guild)
        for key, matched in matches:
            result += f'Matched Name: **{key}**\n'
            for m in matched:
                result += f'> {m.mention} (*{m.joined_at.strftime("%m/%d/%y")}*)\n'
        await ctx.respond(content=result)

    async def _push_roster(self, ctx: discord_ui.SlashedCommand):

        if not await check_permission(ctx, Perm.ADMIN):
            return

        from utils.google_forms import post_enlistment
        users = self.state.users
        await ctx.defer(hidden=True)
        for user in users.users:
            user = users.users[user]
            post_enlistment(user, force=True)
        await ctx.respond('Done.')

        users.save()
