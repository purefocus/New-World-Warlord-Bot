import asyncio
import discord
from dat.EnlistDef import *
from dat.WarStrategy import *
from dat.WarDef import *
from discord_ui import *

from config import *
from utils.botutil import *
from utils.pdfgen import generate_enlistment_pdf


async def cmd_war_select(state, ctx):
    await set_selected_war(state, ctx)


async def cmd_war_make_groups(state, ctx):
    war = await get_def_war(state, ctx)
    if war is not None:
        if war.groups is None:
            war.groups = WarStrategy(war)

        msg = await ctx.respond(embed=war.groups.create_embed())
        war.groups.war_board = MessageReference(msg)

        await ctx.send("done.", hidden=True)
    else:
        await ctx.respond("No war selected!", hidden=True)

    state.save_war_data()


async def cmd_war_assign(state, ctx: SlashedCommand, user_id, group_id, role):
    user_id = str(user_id)
    group_id = str(group_id)
    war = await get_def_war(state, ctx)
    if war is not None:
        groups: WarStrategy = war.groups

        groups.assign_to(user_id, group_id, role)
        await groups.update_boards(state.client)
        await ctx.send("done.", hidden=True)
    else:
        await ctx.respond("No war selected!", hidden=True)
    state.save_war_data()
    print('done')


async def cmd_war_unassign(state, ctx, user_id):
    user_id = str(user_id)
    war = await get_def_war(state, ctx)
    if war is not None and war.groups is not None:
        groups: WarStrategy = war.groups
        groups.unasign(user_id)
        await groups.update_boards(state.client)
        await ctx.send("done.", hidden=True)
    else:
        await ctx.respond("No war selected!", hidden=True)

    state.save_war_data()


async def cmd_war_group_configure(state, ctx, group_id, name):
    group_id = str(group_id)
    war = await get_def_war(state, ctx)
    if war is not None and war.groups is not None:
        groups: WarStrategy = war.groups
        groups.rename_group(group_id, name)
        await groups.update_boards(state.client)
        await ctx.send("done.", hidden=True)
    else:
        await ctx.respond("No war selected!", hidden=True)

    state.save_war_data()


async def cmd_get_enlisted(state, ctx):
    war: WarDef = await select_war(state, ctx, 'Select the war to get the enlistment roster for', allow_multiple=False)
    if war is not None:
        # create_war_roster(war)
        # roster = create_text_war_roster(war)
        file = generate_enlistment_pdf(war)
        await ctx.send(content='Here\'s the roster.', file=discord.File(file))

        # await ctx.send(content=f"```\n{roster}\n```", hidden=True)
    else:
        await ctx.respond(content=f"Denied!", hidden=True)


async def cmd_dl_enlisted(state, ctx):
    war: WarDef = await select_war(state, ctx, 'Select the war to get the enlistment roster for', allow_multiple=False)
    if war is not None:
        file = create_war_roster(war)
        await ctx.send(content='Here\'s the roster.', file=discord.File(file), hidden=True)
    else:
        await ctx.send(content=f"Denied!")
