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


class BtnOpt:
    def __init__(self, key, text, color='blurple'):
        self.key = key
        self.text = text
        self.color = color


async def option_buttons(state: BotState, ctx, question: str, options: list,
                         default_response=None, auto_edit=True, **msg_kwargs):
    msg = None
    try:
        comps = []
        for op in options:
            comps.append(Button(f'btn:options:{op.key}', op.text, color=op.color))

        if isinstance(ctx, discord.Message):
            msg = await ctx.reply(content=question, components=comps, **msg_kwargs)
        else:
            msg = await ctx.send(content=question, components=comps, **msg_kwargs)

        response: discord_ui.PressedButton = await msg.wait_for(event_name='button', client=state.client,
                                                                check=lambda x: _check(x, ctx),
                                                                timeout=60)

        result = default_response
        if 'btn:options:' in response.custom_id:
            result = response.custom_id[12:]

        if auto_edit:
            await msg.edit(content=msg.content + f'\n> Selected: **{response.label}**', components=None)

        await response.respond(ninja_mode=True)

        return result, msg

    except asyncio.TimeoutError as e:
        if 'hidden' in msg_kwargs:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}', hidden=True)
        else:
            await ctx.send(f'You took too long to respond\nDefault Response={default_response}')

        return default_response, msg
