import discord
import asyncio
from discord_ui import *
from bot_state import BotState


async def cmd_bot_configure(state: BotState, ctx: SlashedCommand):
    # TODO: Selection for signup board channel
    # TODO: Selection for war notice channel

    await ctx.respond('Not implemented yet!', hidden=True)
