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
        await msg.edit(contents=f'War \'{war.location}\' has been ended!', components=None)
        state.save_war_data()


async def cmd_repost_war(state, ctx):
    wars, _ = await select_war(state, ctx, 'Select war', allow_multiple=True)
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


def get_field(line: str, fields):
    if ':' in line:
        args = line.split(':', maxsplit=1)
        if args[0] in fields:
            return fields[args[0]], args[1].strip()
    return None, None


from utils.details import get_location


def parse_war_info(state: BotState, lines) -> WarDef:
    result = {}
    for line in lines:
        field, info = get_field(line, war_fields)
        if field is not None:
            result[field] = info

    if len(result) == len(war_fields):
        # print_dict(result)

        war = WarDef()
        war.attacking = result['attacking']
        war.defending = result['defending']
        war.location = get_location(result['location'])
        war.war_time = result['time']
        war.owners = result['owner']

        return war

    return None


signup_fields = {
    'Name': 'name',
    'Faction': 'faction',
    'Company': 'company',
    'Character Level': 'level',
    'Desired Role(s)': 'role',
    'Primary Weapon/Level': 'primary_weapon',
    'Secondary Weapon/Level': 'secondary_weapon',
    'Group Member(s)': 'preferred_group'
}


def parse_signup_info(state: BotState, lines):
    result = {}
    for line in lines:
        field, info = get_field(line, signup_fields)
        if field is not None:
            result[field] = info

    if len(result) == len(signup_fields):
        entry = UserSignup()
        entry.username = result['name']
        entry.faction = result['faction']
        entry.company = result['company']
        entry.level = result['level']
        entry.role = result['role']
        entry.primary_weapon = result['primary_weapon']
        entry.secondary_weapon = result['secondary_weapon']
        entry.preferred_group = result['preferred_group']

        return entry

    return None


async def parse_group_info(state: BotState, lines):
    pass


async def handle_management_message(state: BotState, msg: discord.Message):
    channel: discord.TextChannel = msg.channel

    content: str = msg.content
    lines = content.splitlines()
    war = parse_war_info(state, lines)
    if war is not None:
        war.active = True
        # await msg.reply(embed=war.get_embeded())
        state.add_war(war)
        await add_war_board(war, state)
        state.save_war_data()


async def handle_signup_message(state: BotState, message: discord.Message):
    channel: discord.channel.TextChannel = message.channel
    content: str = message.content
    lines = content.splitlines()
    entry = parse_signup_info(state, lines)

    try:

        if entry is not None:
            # await msg.reply()

            msg: discord_ui.receive.Message = await message.reply(content='What war are you signing up for?',
                                                                  components=[
                                                                      Button(label='Click Here!',
                                                                             custom_id='signup_btn')])

            test = await msg.wait_for('button', state.client, by=message.author, timeout=20)
            await msg.delete()
            war, resp = await select_war(state, test, 'Which war?')
            if not test.responded:
                await test.respond(ninja_mode=True)

            if war is not None:
                war.add_enlistment(entry.to_enlistment())
                await resp.edit(
                    content='You have been signed up!\nDo not forget to sign up at the war board in-game too!',
                    components=None)

            await message.delete()
            await channel.send(embed=entry.embed())

            await update_war_boards(war, state)
            state.save_war_data()

    except Exception as e:
        raise e
