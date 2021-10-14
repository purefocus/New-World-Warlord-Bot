from dat.WarDef import WarDef
from utils.botutil import *
import discord
from bot_state import BotState
from dat.WarDef import *

from utils.colorprint import *


async def cmd_create_war(ctx, attacking, defending, location, time, owner, state):
    war = WarDef()
    war.attacking = attacking
    war.defending = defending
    war.location = location
    war.war_time = time
    war.owners = owner
    war.active = True

    # await war_form(ctx, client, war)

    state.wars[war.location] = war

    await add_war_board(war, state)
    state.save_war_data()

    await ctx.respond(content='War created!', hidden=True)


async def cmd_end_war(state, ctx):
    war = await select_war(state, ctx, 'Select the war to end', allow_multiple=False)
    if war is not None:
        war.active = False
        state.save_war_data()


async def cmd_repost_war(state, ctx):
    wars = await select_war(state, ctx, 'Select war', allow_multiple=True)
    for war in wars:
        await add_war_board(war, state)
        state.save_war_data()


war_fields = {
    'Attackers Faction': 'attacking',
    'Defenders Faction': 'defending',
    'Contact': 'owner',
    'War Time': 'time',
    'Location': 'location'
}


def get_war_field(line: str):
    if ':' in line:
        args = line.split(':')
        print(args)
        if args[0] in war_fields:
            return war_fields[args[0]], args[1]
    return None, None


async def handle_management_message(state, msg: discord.Message):
    channel: discord.TextChannel = msg.channel
    content: str = msg.content
    lines = content.splitlines()
    result = {}
    for line in lines:
        field, info = get_war_field(line)
        if field is not None:
            result[field] = info

    if len(result) == len(war_fields):
        print_dict(result)

        war = WarDef()
        war.attacking = result['attacking']
        war.defending = result['defending']
        war.location = result['location']
        war.war_time = result['time']
        war.owners = result['owner']
        await msg.delete()
        await channel.send(embed=war.get_embeded())
