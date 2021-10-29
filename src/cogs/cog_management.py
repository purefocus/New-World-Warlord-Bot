from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog

from utils.botutil import *

from bot_state import *
from utils.details import get_location

from utils.colorprint import *

war_fields = {
    'attacking faction': 'attacking',
    'defending faction': 'defending',
    'contact': 'owner',
    'war time': 'time',
    'location': 'location',
    'looking for': 'looking_for'
}

war_required_fields = ['attacking', 'defending', 'time', 'location']

signup_fields = {
    'name': 'name',
    'faction': 'faction',
    'company': 'company',
    'character level': 'level',
    'desired role(s)': 'role',
    'primary weapon/level': 'primary_weapon',
    'secondary weapon/level': 'secondary_weapon',
    'group member(s)': 'preferred_group'
}


def parse_line(line: str):
    if ':' in line:
        line = line.split(':', maxsplit=1)
        key = line[0].lower().strip()
        val = line[1].strip()

        if val.lower() == 'none' or len(val) == 0:
            val = None

        return key, val

    return None, None


def get_field(key: str, value: str, fields: dict):
    if key is not None and key in fields:
        return fields[key], value
    return None, None


def parse_text_block(line: str, lines: list, idx: int):
    if '---' in line:
        text = ''
        for line in lines[idx + 1:]:
            if '---' in line:
                if len(text.strip()) < 5:
                    return None
                return text
            text += line + '\n'
    return None


def _gf(data, key):
    if key in data:
        return data[key]
    return None


def parse_war_info(state: BotState, lines) -> WarDef:
    result = {}
    is_fake = False
    additional_info = None
    for i in range(len(lines)):
        line = lines[i]
        key, value = parse_line(line)
        field, info = get_field(key, value, war_fields)

        if '[Fake]' in line:
            is_fake = True

        text_block = parse_text_block(line, lines, i)
        if text_block is not None:
            additional_info = text_block

        if field is not None:
            result[field] = info

    has_fields = True
    for field in war_required_fields:
        if field not in result:
            print(f'does not have {field}')
            print_dict(result)
            has_fields = False

    if has_fields:
        # print_dict(result)
        war = WarDef()
        war.is_fake = is_fake
        war.attacking = _gf(result, 'attacking')
        war.defending = _gf(result, 'defending')
        war.location = get_location(_gf(result, 'location'))
        war.war_time = _gf(result, 'time')
        war.owners = _gf(result, 'owner')
        war.additional_info = additional_info
        lf = _gf(result, 'looking_for')
        if lf is not None:
            war.looking_for = lf.replace(';', '\n')

        return war

    return None


def parse_signup_info(state: BotState, lines):
    result = {}
    for line in lines:

        key, value = parse_line(line)
        field, info = get_field(key, value, signup_fields)

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


def parse_group_info(group: GroupAssignments, lines):
    members = []
    group_id = None
    for i in range(len(lines)):
        line: str = lines[i]

        key, val = parse_line(line)
        if key is None:
            continue

        if key.startswith('group'):
            group_id = key
            group.update_group(group_id, name=val)
            members = []
        elif key.startswith('-') and group_id is not None:
            args = val.split(' ', maxsplit=1)
            if len(args) == 1:
                members.append((args[0], None))
            else:
                args[1] = args[1].replace('(', '').replace(')', '').replace(' ', '')
                members.append((args[0], args[1]))
            group.update_group(group_id, members=members)

    # print_dict(group.__dict__())


async def handle_management_message(state: BotState, msg: discord.Message, edited):
    channel: discord.TextChannel = msg.channel

    content: str = msg.content
    lines = content.splitlines()
    war = parse_war_info(state, lines)
    print(war)

    if war is not None:
        war.active = True
        print('1')
        parse_group_info(war.groups, lines)
        print('2')
        if war.is_fake:
            print('Fake!')
            await msg.reply(embed=war.get_embeded())
            return True

        existed = state.add_war(war, edit=edited)
        if existed and edited:
            try:
                await update_war_boards(war, state)
            except:
                await add_war_board(war, state, msg)
        else:
            await add_war_board(war, state, msg)

        state.save_war_data()
        return True

    return False


async def handle_signup_message(state: BotState, message: discord.Message, edited):
    channel: discord.channel.TextChannel = message.channel
    content: str = message.content
    lines = content.splitlines()
    entry = parse_signup_info(state, lines)

    try:

        if entry is not None:
            # await msg.reply()

            msg = await message.reply(content='What war are you signing up for?',
                                      components=[
                                          Button(label='Click Here!',
                                                 custom_id='signup_btn')])

            test = await msg.wait_for('button', state.client, by=message.author, timeout=20)
            await msg.delete()
            war, resp = await select_war(state, test, 'Which war?')
            if not test.responded:
                await test.respond(ninja_mode=True)

            if war is not None:
                await state.add_enlistment(war, entry)
                war.add_enlistment(entry.to_enlistment())
                await resp.edit(
                    content='You have been signed up!\nDo not forget to sign up at the war board in-game too!',
                    components=None)

            # await message.delete()
            # await channel.send(embed=entry.embed())

            # await update_war_boards(war, state)
            # state.save_war_data()
            return True

    except Exception as e:
        raise e
    return False


class WarManagementCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

    async def process_messages(self, msg: discord.Message, edited):
        # Only process if the bot was mentioned
        if self.client.user.mentioned_in(msg):

            try:
                if msg.author == self.client.user:
                    return

                ret = False

                if self.state.config.is_war_management(msg):
                    ret = await handle_management_message(self.state, msg, edited)

                if self.state.config.is_war_signup(msg):
                    ret = await handle_signup_message(self.state, msg, edited)

                if ret:
                    msg = await msg.reply(content='Done.')
                    await msg.delete(delay=1)

            except Exception as e:
                import traceback
                import sys
                traceback.print_exception(*sys.exc_info())

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        await self.process_messages(msg, False)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        await self.process_messages(after, True)

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
        try:
            if payload.cached_message is not None:
                return

            data = payload.data
            if data['author']['id'] == str(self.client.user.id):
                return

            mentions = data['mentions']
            if mentions is not None:
                for mention in mentions:

                    if mention['id'] == str(self.client.user.id):
                        channel = self.client.get_channel(payload.channel_id)
                        msg = await channel.fetch_message(payload.message_id)
                        if msg is not None:
                            await handle_management_message(self.state, msg, True)
            # print_dict(payload.data)
        except Exception as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())