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

BOT_CONFIG_HELP = '```' \
                  '/warlord_cfg options:<set|help>\n' \
                  '      help [Displays this help message]\n' \
                  '      set:\n' \
                  '        signup [sets the current channel to the signup channel (Where users can sign up for wars)]\n' \
                  '        notice [sets the current channel to the war notice channel (Where war notice boards will appear)]\n' \
                  '        management [sets the current channel to the war management channel (Where you can manage wars and group assignments)]\n' \
                  '```'


def _set_channel(state: BotState, ctx: Interaction, key: str):
    guild_id = ctx.guild_id
    cfg: GuildConfig = state.config.guildcfg(guild_id)
    if cfg is not None:
        channel = ctx.channel
        if cfg.set_channel(key, channel):
            state.config.save()
            return True
    return False


channel_config_options = '[notice, management, signup]'


class ConfigurationCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    @subslash_cog(base_names=['warlord_cfg', 'set'], name='channel', options=[
        SlashOption(str, name='channel', description=channel_config_options, required=True)
    ])
    async def cmd_set_channel_notice(self, ctx: Interaction, channel: str):
        if check_permission(ctx, Perm.CONFIGURE):
            if _set_channel(self.state, ctx, channel):
                response = f'{channel} channel has been set to {ctx.channel.name}'
            else:
                response = f'Unknown channel configuration key {channel}!\n Available options are {channel_config_options}'
            await ctx.respond(content=response, hidden=True)

    @subslash_cog(base_names=['warlord_cfg', 'post'], name='world-status')
    async def cmd_post_world_status(self, ctx: Interaction, channel: str):
        if check_permission(ctx, Perm.CONFIGURE):
            msg = await ctx.channel.send(content='World Status Here')
            self.state.config.register_message('world-status', msg)
            await ctx.respond(content='-', hidden=True)

    @subslash_cog(base_names=['warlord_cfg', 'server'], name='init')
    async def cmd_init_guild(self, ctx: Interaction):
        if check_permission(ctx, Perm.CONFIGURE):
            if self.state.config.guildcfg(ctx.guild_id) is not None:
                response = '[Error] This guild has already been registered'
            else:
                self.state.config.add_guild(ctx.guild)
                response = 'Guild Registered!'

            await ctx.respond(response, hidden=True)


# async def cmd_bot_configure(state: BotState, ctx: SlashedCommand, options: str):
#     if not check_permission(ctx, Perm.CONFIGURE):
#         return
#     try:
#         options = options.strip()
#         options = options.split(' ')
#         print(options)
#         response = None
#
#         if len(options) == 0 or options[0] == '?' or options[0] == 'help':
#             await ctx.respond(content=BOT_CONFIG_HELP, hidden=True)
#
#         else:
#             # if options[0] == 'set':
#             #     if len(options) < 2:
#             #         response = '[Error] No configuration property specified!'
#             #     else:
#             #         prop = options[1]
#             #         if _set_channel(state, ctx, prop):
#             #             response = f'{prop} channel has been set to {ctx.channel.name}'
#             #         else:
#             #             response = f'[Error] Unknown configuration property: {prop}'
#
#             # if options[0] == 'init':
#             #     if state.config.guildcfg(ctx.guild_id) is not None:
#             #         response = '[Error] This guild has already been registered'
#             #     else:
#             #         state.config.add_guild(ctx.guild)
#             #         response = 'Guild Registered!'
#
#             if options[0] == 'status':
#                 msg = await ctx.channel.send(content='World Status Here')
#                 state.config.register_message('world-status', msg)
#                 await ctx.respond(content='-', hidden=True)
#
#         if response is not None:
#             await ctx.respond(content=response, hidden=True)
#
#     except Exception as e:
#         await ctx.respond(content=e, hidden=True)
