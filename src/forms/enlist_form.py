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

    selected_wars, sel_msg = await select_war(state, ctx, 'Select which war to enlist in', allow_multiple=True)
    if len(selected_wars) > 0:
        enlistment = await enlist_form(ctx, state.client, enlistment, sel_msg)

        if enlistment is None:
            print(f'Finished Enlisting {username} ({level}) [{company}] FAILED')
            return
        for war in selected_wars:
            if war.add_enlistment(enlistment.copy()):
                await sel_msg.edit(content=f'your enlistment application for **{war}** has been updated!',
                                   components=None)
            else:
                await sel_msg.edit(content=f'your enlistment application for **{war}** has been submitted!',
                                   components=None)
            await update_war_boards(war, state)

        state.save_war_data()

        for ch in state.config.get_signup_channels():
            await ch.send(embed=enlistment.create_embed())

        # await ctx.send(content=f'You have been successfully enlisted in the war(s):\n {selected_wars}', hidden=True)
    print(f'Finished Enlisting {username} ({level}) [{company}]')


async def ask_weapons_for_role(ctx, client, role, msg):
    await msg.edit(f'What are your weapons for the {role} role?', components=[
        [SelectMenu('pw', options=weapon_select_options, placeholder='Primary Weapon')],
        [SelectMenu('sw', options=weapon_select_options, placeholder='Secondary Weapon')]
    ])

    primary_weapon = None
    secondary_weapon = None
    while True:
        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)
        if menu.custom_id == 'pw':
            primary_weapon = menu.selected_options[0].label
        if menu.custom_id == 'sw':
            secondary_weapon = menu.selected_options[0].label
        if primary_weapon is not None and secondary_weapon is not None:
            break

    return role, primary_weapon, secondary_weapon


async def enlist_form(ctx: SlashedCommand, client, enlistment, msg):
    # embed_msg: discord.Message = await ctx.send(embed=enlistment.create_embed(), hidden=True)

    try:
        await msg.edit('What is your faction?', components=[
            SelectMenu('faction', options=faction_select_options, placeholder='Select Faction')
        ])
        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)
        enlistment.faction = menu.selected_options[0].label

        await msg.edit('What role can you fill?', components=[
            SelectMenu('role', options=role_select_options, placeholder='Desired Role', max_values=1)  # len(WAR_ROLES))
        ])

        menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
        await menu.respond(ninja_mode=True)

        roles = [x.label for x in menu.selected_options]

        enlistment.roles = {}
        for role in roles:
            r, pw, sw = await ask_weapons_for_role(ctx, client, role, msg)
            enlistment.roles[r] = f'{pw}/{sw}'
            # await embed_msg.edit(embed=enlistment.create_embed())
        return enlistment

    except asyncio.TimeoutError:
        await msg.edit(content="you took too long to choose", components=None)
    return None
