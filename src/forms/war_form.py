import asyncio
import discord
from discord_ui import *
from dat.WarDef import WarDef

location_choices = ['Brightwood', 'Cutlass Keys', 'Ebonscale Reach',
                    'Everfall', 'First Light', 'Monarch\'s Bluff',
                    'Mourningdale', 'Reekwater', 'Restless Shore',
                    'Weaver\'s Fen', 'Windsward']

location_options = [SelectOption(i, x) for (i, x) in enumerate(location_choices)]


async def war_form(ctx, client, war: WarDef):
    msg = await ctx.send('Where is this war going to be held?', components=[
        SelectMenu('location', options=location_options, placeholder='Location')
    ], hidden=True)

    menu: SelectedMenu = await msg.wait_for('select', client, timeout=60)
    await menu.respond(ninja_mode=True)

    war.location = menu.selected_options[0].label

    msg = await ctx.send('')
