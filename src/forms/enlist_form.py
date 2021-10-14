import asyncio
import discord
from dat.EnlistDef import *
from discord_ui import *

from config import *
from utils.botutil import *

weapon_select_options = [SelectOption(i, x) for (i, x) in enumerate(WEAPON_CHOICES)]
role_select_options = [SelectOption(i, x) for (i, x) in enumerate(WAR_ROLES)]
faction_select_options = [SelectOption(i, x) for (i, x) in enumerate(FACTIONS)]


async def cmd_enlist(state, ctx, username, level, company):
    enlistment = Enlistment()
    enlistment.username = username
    enlistment.level = level
    enlistment.company = company

    print(f'Started Enlisting {username} ({level}) [{company}]')

    selected_wars = await select_war(state, ctx, 'Select which war to enlist in', allow_multiple=True)
    if len(selected_wars) > 0:
        enlistment = await enlist_form(ctx, state.client, enlistment)

        for war in selected_wars:
            if war.add_enlistment(enlistment.copy()):
                await ctx.send(content=f'your enlistment application for **{war}** has been updated!', hidden=True)
            else:
                await ctx.send(content=f'your enlistment application for **{war}** has been submitted!', hidden=True)
            await update_war_boards(war, state)

        state.save_war_data()

        for ch in state.config.get_signup_channels(state.client):
            discord.Message = await ch.send(embed=enlistment.create_embed())

        # await ctx.send(content=f'You have been successfully enlisted in the war(s):\n {selected_wars}', hidden=True)
    print(f'Finished Enlisting {username} ({level}) [{company}]')


async def ask_weapons_for_role(ctx, client, role):
    msg = await ctx.send(f'What are your weapons for the {role} role?', components=[
        [SelectMenu('pw', options=weapon_select_options, placeholder='Primary Weapon')],
        [SelectMenu('sw', options=weapon_select_options, placeholder='Secondary Weapon')]
    ], hidden=True)

    primary_weapon = None
    secondary_weapon = None
    while True:
        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)
        print('id', menu.custom_id)
        if menu.custom_id == 'pw':
            primary_weapon = menu.selected_options[0].label
        if menu.custom_id == 'sw':
            secondary_weapon = menu.selected_options[0].label
        if primary_weapon is not None and secondary_weapon is not None:
            break

    return role, primary_weapon, secondary_weapon


async def enlist_form(ctx, client, enlistment):
    # embed_msg: discord.Message = await ctx.send(embed=enlistment.create_embed(), hidden=True)

    try:
        msg = await ctx.send('What is your faction?', components=[
            SelectMenu('faction', options=faction_select_options, placeholder='Select Faction')
        ], hidden=True)

        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)
        enlistment.faction = menu.selected_options[0].label

        msg = await ctx.send('What roles can you fill?', components=[
            SelectMenu('role', options=role_select_options, placeholder='Desired Roles', max_values=len(WAR_ROLES))
        ], hidden=True)

        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)

        roles = [x.label for x in menu.selected_options]

        enlistment.roles = {}
        for role in roles:
            r, pw, sw = await ask_weapons_for_role(ctx, client, role)
            enlistment.roles[r] = f'{pw}/{sw}'
            # await embed_msg.edit(embed=enlistment.create_embed())

    except asyncio.TimeoutError:
        await ctx.send(content="you took too long to choose", hidden=True)
    return enlistment
