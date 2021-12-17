import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog, context_cog
from bot_state import BotState

# from dat.datadef import *
from dat.WarDef import WarDef
from database.tables.users_table import UserRow

from discord_ui import *

from utils.colorprint import *
from utils.details import WAR_ROLES, WEAPON_CHOICES, FACTIONS
from utils.details import replace_company_name
from views.embeds import user_embed

# from dat.UserSignup import UserSignup
from dat.UserProfile import UserProfile

from views.view_confirm import *

import asyncio
import config as cfg
from utils.permissions import *
from utils.botutil import print_stack_trace

question_list = {
    'name': {
        'question': '**What is your character name?**',
        'response_type': str,
    },
    'level': {
        'question': '**What is your gear score?**',
        'response_type': int,
        'check': lambda response, answers: None if 0 < response <= 1000 else 'Your answer must be between 0-600'
    },
    # 'gearscore': {
    #     'question': 'What level is your Gear Score?',
    #     'response_type': int,
    #     'askif': lambda answers: answers['level'] == 60
    # },
    'faction': {
        'question': '**What Faction are you?**',
        'choices': FACTIONS,
    },
    'company': {
        'question': '**What Company are you in?**',
        'response_type': str,
    },
    'role': {
        'question': '**What is your desired role?**',
        'choices': WAR_ROLES,
    },
    'primary_weapon': {
        'question': '**What is your Primary Weapon?**',
        'choices': WEAPON_CHOICES,
    },
    # 'primary_level': {
    #     'followup': lambda x: f"What is your Mastery Level for your {x['primary_weapon']}",
    #     'response_type': int,
    #     'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    # },
    'secondary_weapon': {
        'question': '**What is your Secondary Weapon?**',
        'choices': WEAPON_CHOICES,
        'check': lambda response, answers: None if response != answers[
            'primary_weapon'] else 'You must select a different weapon from your primary!'
    },
    # 'secondary_level': {
    #     'followup': lambda x: f"What is your Mastery Level for your {x['secondary_weapon']}",
    #     'response_type': int,
    #     'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    # },
    'group': {
        'question': '**Any extra information?** \n  *Attribute Distribution, Specialties, Favorite Taylor Swift song, etc..?*\n*Enter None if no extra information*',
        'response_type': str,
    }
}
STR_ENLIST_FAILED = 'Something went wrong and you have not been enlisted.'

STR_NO_ACTIVE_WAR = 'Sorry, This war is no longer active!\nIf this is a mistake, please contact an admin!'

STR_ENLIST_SUCCESS = 'You have successfully been enlisted for the war **%s**\n ' \
                     'You can update you enlistment by clicking the \'Click to Enlist!\' button again.\n' \
                     '**Do not forget to also sign up at the in-game war board!**'

STR_ENLIST_ABSENT = 'You have successfully been marked **absent** for the war **%s**\n ' \
                    'You can update you enlistment by clicking the \'Click to Enlist!\' button again.\n'

STR_NO_PERMISSION = 'It seems you have privacy settings preventing me from sending you a private message!\n' \
                    'Please manually enter your information using the following template and try again!\n' \
                    '```\n' \
                    '@Warlord\n' \
                    'Name: \n' \
                    'Faction: \n' \
                    'Company: \n' \
                    'Character Level: \n' \
                    'Desired Role: \n' \
                    'Primary Weapon: \n' \
                    'Secondary Weapon: \n' \
                    'Extra Information: \n' \
                    '```\n' \
                    'Once you have done this, try and enlist again!'

cancel_btn = BtnOpt('cancel', 'Cancel', 'red')
update_btn = BtnOpt('survey', 'Update', 'blurple')
survey_btn = BtnOpt('survey', 'Signup', 'green')
enlist_btn = BtnOpt('enlist', 'Signup', 'green')
absent_btn = BtnOpt('absent', 'Absent', 'green')

test_responses = {
    'name': 'purefocus',
    'level': '582',
    'faction': 'Syndicate',
    'company': 'Storm Chasers',
    'role': 'Str DPS',
    'primary_weapon': 'War Hammer',
    'secondary_weapon': 'Great Axe',
    'group': None

}


# def _check(x, ctx):


async def question(client: commands.Bot, ctx, answers,
                   question=None, followup=None, response_type=None, choices=None,
                   check=None, key=None, **kwargs) -> (str, object):
    if followup is not None:
        question = followup(answers)

    response = None
    components = None
    if choices is not None:
        options = []
        for choice in choices:
            options.append(SelectOption(value=choice, label=choice))
        components = [
            SelectMenu(custom_id='question_select', options=options, min_values=1, max_values=1, placeholder=question)
        ]

    msg = await ctx.author.send(content=f'{question}', components=components)

    if choices is not None:
        selection: SelectedMenu = await msg.wait_for('select', client=client, by=ctx.author, timeout=120)

        value = selection.selected_values[0]
        if not selection.responded:
            await selection.respond(ninja_mode=True)

        await msg.edit(content=f'**Selected**: *{value}*', components=None)

        response = value
    else:
        test: discord.Message = await client.wait_for('message',
                                                      check=lambda x: x.author == ctx.author and
                                                                      x.channel.type == discord.ChannelType.private,
                                                      timeout=120)

        response = test.content
        if response_type == int:
            response = response.strip()
            try:
                response = int(response)
            except:
                await ctx.author.send(content='Invalid input! Input should be a **number**!')
                response = None
    if check is not None:
        check_response = check(response, answers)
        if check_response is not None:
            await ctx.author.send(content=f'Invalid input! {check_response}')
            response = None

    return key, response


class DMEnlistmentCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState):
        self.client = client
        self.state = state

        self.users_enlisting = {}

    async def enlist_questionair(self, war, ctx, udata=None) -> [UserRow, None]:
        try:
            gcfg = self.state.config.guildcfg(ctx.guild_id)
            if gcfg is None:
                return
            user = UserProfile(ctx.author, gcfg)

            responses = {}
            # responses = test_responses
            if user.username is not None:
                responses['name'] = user.username

                if user.company is not None:
                    responses['faction'] = 'Syndicate'
                    # responses['company'] = user.company

            if udata is not None:
                user.username = responses['name'] = udata.username
                user.faction = responses['faction'] = udata.faction
                # user.company = responses['company'] = udata.company
                # if udata.level == 60:
                #     user.level = responses['level'] = udata.level

            await ctx.author.send(
                f'Hello **{user}**, you have chosen to enlist in the war for **{war.location}**'
                f'\n*This information will be saved to make it faster to sign up in the future!*\n'
                f'\nPlease answer the following questions:\n')

            for q in question_list:
                if q in responses:
                    continue

                ques = question_list[q]
                if 'askif' in ques and not ques['askif'](responses):
                    continue
                key, response = None, None
                while response is None:
                    key, response = await question(self.client, ctx, responses, key=q, **ques)
                    if key is None:
                        return None
                responses[key] = response

            await ctx.author.send('You have finished answering all the questions!')

            # user = UserSignup()
            u = UserRow()
            u.discord = user.discord_user
            u.faction = responses['faction']
            u.company = responses['company']
            print('c1: ', u.company)
            u.company = replace_company_name(user.company)
            print('c2: ', u.company)
            u.role = responses['role']
            u.username = responses['name']
            u.level = responses['level']
            # if 'gearscore' in responses:
            #     user.level = responses['gearscore']

            u.weapon1 = f"{responses['primary_weapon']}"  # ({responses['primary_level']})"
            u.weapon2 = f"{responses['secondary_weapon']}"  # ({responses['secondary_level']})"
            pref_group = responses['group']
            if pref_group is not None and pref_group.lower() == 'none':
                pref_group = None
            u.preferred_group = pref_group
            print_dict(responses, 'Response')
            print_dict(u.__dict__, 'RowData')

            return u  # .to_enlistment()

        except discord.Forbidden as e:
            print('No permission!')
            await ctx.send(STR_NO_PERMISSION, hidden=True)
        except asyncio.TimeoutError as e:

            print(colors.red(f'[TimeoutError] Failed to enlist {ctx.author.display_name}!'))

        return None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.client.user:
            return

        channel = msg.channel
        if channel.type != discord.ChannelType.private:
            return

    async def determine_action(self, user: UserProfile, war: WarDef, ctx: Interaction, absent=False):

        if war is not None:
            in_war = user.username in war.roster
            in_absent = user.username in war.absent
            user_data: UserRow = user.user_data
            data_exists = user_data is not None
            question_options = []

            question = 'If you see this message, contact an administrator!'
            embed = None

            gname = ''
            try:
                gname = ctx.guild.name
            except:
                pass

            print_fields('Enlistment', user=user.discord_user, username=user.username, in_war=in_war,
                         in_absent=in_absent, data_exists=data_exists, guild=gname)

            if not data_exists:
                question = 'Before you can sign up, we need to collect some information first!'
                question_options.append(survey_btn)

            elif in_war:
                if absent:
                    question = f'You are currently signed up for this war, are you sure you would like to switch to Absent? (**{war.location}**)'
                    question_options.append(absent_btn)
                else:
                    question = f'You are already enlisted in this war, would you like to update your information? (**{war.location}**)'
                    embed = user_embed(user_data, self.state)
                    question_options.append(update_btn)
            else:
                if absent:
                    question = f'Are you sure you want to be marked absent for this war? (**{war.location}**)'
                    question_options.append(absent_btn)
                else:
                    question = f'Is the following information correct?\nWould you like to update your information?'
                    embed = user_embed(user_data, self.state)
                    question_options.append(enlist_btn)
                    question_options.append(update_btn)

                if in_absent and absent:
                    await ctx.respond('You are already marked absent for this war! (**{war.location}**)', hidden=True)
                    return None, None

            question_options.append(cancel_btn)
            response, msg = await option_buttons(self.state, ctx,
                                                 question=question,
                                                 options=question_options,
                                                 embed=embed,
                                                 hidden=True)

            return response, msg
        return None, None

    async def _do_enlist(self, war: WarDef, ctx: Interaction, absent=False):
        try:
            gcfg = self.state.config.guildcfg(ctx.guild_id)

            if gcfg is None:
                return

            user = UserProfile(ctx.author, gcfg, self.state.users)
            response, action_msg = await self.determine_action(user, war, ctx, absent)

            print_fields('Enlist Response', username=user.username, response=response)

            if response is None:
                print(colors.red('Response is None!'))
                return

            if response == 'survey':
                user.user_data = await self.enlist_questionair(war, ctx, user.user_data)
                if user.user_data is None:
                    await action_msg.edit(
                        f'You took too long to respond to the messages! Try again or message an admin for assistance!',
                        components=None, embed=None)
                else:
                    await self.state.add_enlistment(str(ctx.author), war, user.user_data, absent=absent, announce=False)
                    if absent:
                        await action_msg.edit(f'You have been marked **Absent** for the war at **{war.location}**',
                                              components=None, embed=None)

                    else:
                        await action_msg.edit(f'You have been marked **Enlisted** for the war at **{war.location}**',
                                              components=None, embed=user_embed(user.user_data, self.state))

            elif response == 'enlist':
                await self.state.add_enlistment(str(ctx.author), war, user.user_data, absent=absent, announce=False)
                await action_msg.edit(f'You have been marked **Enlisted** for the war at **{war.location}**',
                                      components=None, embed=user_embed(user.user_data, self.state))

            elif response == 'absent':
                await self.state.add_enlistment(str(ctx.author), war, user.user_data, absent=True, announce=False)
                await action_msg.edit(f'You have been marked **Absent** for the war at **{war.location}**',
                                      components=None, embed=None)

            elif response == 'cancel':
                pass
        except:
            print_stack_trace()

    async def _proc_enlist(self, ctx, war, absent=False):
        if str(ctx.author) in self.users_enlisting:
            proc = self.users_enlisting[str(ctx.author)]
            if proc is not None:
                proc.close()
                print('Proc killed')
            del self.users_enlisting[str(ctx.author)]

        self.users_enlisting[str(ctx.author)] = self._do_enlist(war, ctx, absent)
        print(colors.red('Users Enlisting: '), len(self.users_enlisting))
        await self.users_enlisting[str(ctx.author)]
        try:
            del self.users_enlisting[str(ctx.author)]
            print(colors.red('Users Enlisting: '), len(self.users_enlisting))
        except:
            pass

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):

        try:
            data = ctx.data
            if 'custom_id' not in data:
                return
            if not await check_permission(ctx, Perm.ENLIST):
                return
            id: str = data['custom_id']
            absent = id.startswith('btn:absent:')
            if id.startswith('btn:enlist:') or absent:
                id = id[11:]
                war = None
                for w in self.state.wars:
                    w = self.state.wars[w]
                    if w.id == id:
                        war = w
                        break
            else:
                return

            await self._proc_enlist(ctx, war, absent)

        except:
            print('error: ', ctx.author)
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    @slash_cog(description='Enlist yourself to participate in wars!', **cfg.cmd_cfg)
    async def enlist(self, ctx: SlashedCommand):
        if not await check_permission(ctx, Perm.ENLIST):
            return
        try:
            war = self.state.wars['General Enlistment']
            await self._proc_enlist(ctx, war)
        except:

            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    @context_cog(type="user", name="Enlistment Lookup")
    async def enlistment_lookup(self, ctx, user: discord.Member):
        print('Enlistment Lookup! ', str(user))

        data: UserRow = self.state.users[str(user)]
        if data is not None:
            await ctx.respond(content=' ', embed=user_embed(data, self.state), hidden=True)
        else:
            await ctx.respond(content='No enlistment data found for this user!', hidden=True)
