import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState
import asyncio
import discord_ui
from discord_ui import Button


async def ask_confirm(state: BotState, ctx: discord_ui.SlashedCommand, question: str, default_response=False, ret_msg=False):
    try:
        comps = [
            Button('btn:confirm_yes', 'Yes'),
            Button('btn:confirm_no', 'No')
        ]
        msg = await ctx.send(content=question, components=comps, hidden=True)

        response = await msg.wait_for(event_name='button', client=state.client, timeout=60)
        result = default_response
        if response.custom_id == 'btn:confirm_yes':
            result = True
        elif response.custom_id == 'btn:confirm_no':
            result = False

        await response.respond(ninja_mode=True)

        if not ret_msg:
            await msg.edit(content=f'{question}\n **You responded: {"Yes" if result else "No"}**', components=None)

            return result
        return result, msg

    except asyncio.TimeoutError as e:
        await ctx.send(f'You took too long to respond\nDefault Response={default_response}')
