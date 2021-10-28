from dat.WarDef import WarDef
from dat.UserSignup import *
from utils.botutil import *
import discord
from bot_state import BotState
from dat.WarDef import *
# from forms.signup_view import SignupButton

import discord_ui

from utils.colorprint import *


async def cmd_create_war(ctx, attacking, defending, location, time, owner, state: BotState):
    war = WarDef()
    war.attacking = attacking
    war.defending = defending
    war.location = location
    war.war_time = time
    war.owners = owner
    war.active = True

    # await war_form(ctx, client, war)

    state.add_war(war)

    await add_war_board(war, state)
    state.save_war_data()

    await ctx.respond(content='War created!', hidden=True)


async def cmd_end_war(state, ctx):
    war, msg = await select_war(state, ctx, 'Select the war to end', allow_multiple=False)
    if war is not None:
        war.active = False
        await msg.edit(content=f'War \'{war.location}\' has been ended!', components=None)
        for board in war.boards:
            m = await board.get_message(state.client)
            if m is not None:
                await m.delete()
        # state.save_war_data()


async def cmd_repost_war(state, ctx):
    wars, _ = await select_war(state, ctx, 'Select war', allow_multiple=True)
    for war in wars:
        for board in war.boards:
            try:
                msg = await board.get_message(state.client)
                if msg is not None:
                    await msg.delete()
                board.valid = False
            except:
                pass
        await add_war_board(war, state)
        state.save_war_data()


async def cmd_post_war(state, ctx):
    wars, _ = await select_war(state, ctx, 'Select war', allow_multiple=True)
    for war in wars:
        await add_war_board_to(war, state, ctx.channel)
        state.save_war_data()


async def cmd_post_btn(state, ctx: SlashedCommand):
    wars, msg = await select_war(state, ctx, 'Select war', allow_multiple=True)
    btns = []
    for war in wars:
        btns.append(
            Button(
                custom_id=f'btn:enlist:{war.id}',
                label=f'Enlist for {war.location}',
                new_line=True
            )
        )
    await msg.edit(content='Done!', components=None)
    await ctx.respond(content='**Click buttons to enlist!**', components=btns)
