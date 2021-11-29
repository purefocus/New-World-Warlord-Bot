import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState
import asyncio
import discord_ui
from discord_ui import Button


def _check(x, ctx):
    print(type(x), type(ctx))
    if isinstance(ctx, discord.Member):
        return x.author == ctx
    return x.author == ctx.author


async def ask_confirm(state: BotState, ctx, question: str, embed: discord.Embed = None, text=None, colors=None,
                      default_response=False, ret_msg=False, hidden=True, cancel=False):
    try:
        if text is None:
            text = ['Yes', 'No', 'Cancel']
        if colors is None:
            colors = ['green', 'red', 'red']

        comps = [
            Button('btn:confirm_yes', text[0], color=colors[0]),
            Button('btn:confirm_no', text[1], color=colors[1])
        ]
        if cancel:
            comps.append(Button('btn:confirm_cancel', text[-1], color=colors[-1]))

        if hidden:
            msg = await ctx.send(content=question, components=comps, embed=embed, hidden=hidden)
        elif isinstance(ctx, discord.Message):
            msg = await ctx.reply(content=question, components=comps, embed=embed)
        else:
            msg = await ctx.send(content=question, components=comps, embed=embed)

        response = await msg.wait_for(event_name='button', client=state.client,
                                      check=lambda x: _check(x, ctx),
                                      timeout=60)
        result = default_response
        if response.custom_id == 'btn:confirm_yes':
            result = True
        elif response.custom_id == 'btn:confirm_no':
            result = False
        elif response.custom_id == 'btn:confirm_cancel':
            result = None

        await response.respond(ninja_mode=True)

        if not ret_msg:
            await msg.edit(content=f'{question}\n **You responded: {"Yes" if result else "No"}**', components=None,
                           embed=None)

            return result
        return result, msg

    except asyncio.TimeoutError as e:
        if hidden:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}', hidden=hidden)
        else:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}')


async def option_buttons(state: BotState, ctx, question: str, options: list, embed: discord.Embed = None,
                         default_response=None, ret_msg=False, hidden=True, cancel=False):
    try:
        comps = []
        for text, color, key in options:
            comps.append(Button(f'btn:options:key', text, color=color))

        if hidden:
            msg = await ctx.send(content=question, components=comps, embed=embed, hidden=hidden)
        elif isinstance(ctx, discord.Message):
            msg = await ctx.reply(content=question, components=comps, embed=embed)
        else:
            msg = await ctx.send(content=question, components=comps, embed=embed)

        response = await msg.wait_for(event_name='button', client=state.client,
                                      check=lambda x: _check(x, ctx),
                                      timeout=60)

        result = default_response
        if 'btn:options:' in response.custom_id:
            result = response.custom_id[14:]

        await response.respond(ninja_mode=True)

        if not ret_msg:
            await msg.edit(content=f'{question}\n **You responded: {"Yes" if result else "No"}**', components=None,
                           embed=None)

            return result
        return result, msg

    except asyncio.TimeoutError as e:
        if hidden:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}', hidden=hidden)
        else:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}')
