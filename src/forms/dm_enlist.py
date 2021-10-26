import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

from dat.datadef import *

from discord_ui import *

from utils.colorprint import *
from utils.details import WAR_ROLES, WEAPON_CHOICES, FACTIONS

from dat.UserSignup import UserSignup
from dat.UserProfile import UserProfile

from views.view_confirm import ask_confirm

import asyncio

question_list = {
    'name': {
        'question': 'What is your character name?',
        'response_type': str,
    },
    'level': {
        'question': 'What level is your character?',
        'response_type': int,
        'check': lambda response, answers: None if 0 < response <= 60 else 'Your answer must be between 0-60'
    },
    'gearscore': {
        'question': 'What level is your Gear Score?',
        'response_type': int,
        'askif': lambda answers: answers['level'] == 60,
        'check': lambda response, answers: None if 0 < response <= 60 else 'Your answer must be between 0-60'
    },
    'faction': {
        'question': 'What Faction are you?',
        'choices': FACTIONS,
    },
    'company': {
        'question': 'What Company are you in?',
        'response_type': str,
    },
    'role': {
        'question': 'What is your desired role?',
        'choices': WAR_ROLES,
    },
    'primary_weapon': {
        'question': 'What is your Primary Weapon?',
        'choices': WEAPON_CHOICES,
    },
    'primary_level': {
        'followup': lambda x: f"What is your Mastery Level for your {x['primary_weapon']}",
        'response_type': int,
        'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    },
    'secondary_weapon': {
        'question': 'What is your Secondary Weapon?',
        'choices': WEAPON_CHOICES,
        'check': lambda response, answers: None if response != answers[
            'primary_weapon'] else 'You must select a different weapon from your primary!'
    },
    'secondary_level': {
        'followup': lambda x: f"What is your Mastery Level for your {x['secondary_weapon']}",
        'response_type': int,
        'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    },
    'group': {
        'question': 'Do you have a preferred group? Enter `None` if you do not have one.',
        'response_type': str,
    }
}
STR_ENLIST_FAILED = 'Something went wrong and you have not been enlisted.'
STR_NO_ACTIVE_WAR = 'Sorry, This war is no longer active!\nIf this is a mistake, please contact an admin!'
STR_ENLIST_SUCCESS = 'You have successfully been enlisted for the war **{}**\n ' \
                     'You can update you enlistment by clicking the \'Enlist Now!\' button again.'


async def question(client: commands.Bot, ctx, answers,
                   question=None, followup=None, response_type=None, choices=None,
                   check=None, key=None) -> (str, object):
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

    msg = await ctx.author.send(content=f'**{question}**', components=components)

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

    async def enlist_questionair(self, war, ctx):
        try:
            user = UserProfile(ctx.author)

            await ctx.author.send(
                f'Hello **{user.username}**, you have chosen to enlist in the war for **{war.location}**'
                f'\n*This information will be saved to make it faster to sign up in the future!*\n'
                f'\nPlease answer the following questions:\n')
            responses = {}

            responses['username'] = user.username
            if user.company is not None:
                responses['faction'] = 'Syndicate'
                responses['company'] = user.company

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
                        return False
                responses[key] = response

            # print_dict(responses)
            user = UserSignup()
            user.faction = responses['faction']
            user.company = responses['company']
            user.role = responses['role']
            user.username = responses['name']
            user.level = responses['level']
            user.primary_weapon = f"{responses['primary_weapon']} ({responses['primary_level']})"
            user.secondary_weapon = f"{responses['secondary_weapon']} ({responses['secondary_level']})"
            user.preferred_group = responses['group']

            return user

        except asyncio.TimeoutError as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())
        return None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.client.user:
            return

        channel = msg.channel
        if channel.type != discord.ChannelType.private:
            return

    async def do_enlist(self, war: WarDef, ctx: Interaction):
        # war = self.state.wars[id]
        if war is not None:
            print('Enlistment Started!')
            self.users_enlisting[ctx.author] = True

            msg = None
            ask = True
            user = self.state.users[ctx.author.display_name]
            if user is not None:
                ask, msg = ask_confirm(self.state, ctx,
                                       'You have enlisted in a previous war, so we can just reuse that information! '
                                       '\nWould you like to update your information instead? '
                                       '\n\n*Note: Select **Yes** if you are enlisting someone else!*',
                                       embed=user.embed(), ret_msg=True)
            if ask:
                if not ctx.responded:
                    await ctx.respond(ninja_mode=True)
                user = await self.enlist_questionair(war, ctx)

                if user is not None:
                    ask, msg = await ask_confirm(self.state, ctx, 'Is this information correct?',
                                                 embed=user.embed(), ret_msg=True)
            else:
                success = True

            del self.users_enlisting[ctx.author]
            print('Enlistment Ended! ', len(self.users_enlisting))

            if user is not None:
                await self.state.add_enlistment(war, user, announce=ask)
                if msg is not None:
                    await msg.edit(content=STR_ENLIST_SUCCESS % war.location, components=None)
                else:

                    await ctx.author.send(content=STR_ENLIST_SUCCESS % war.location)
            else:
                await ctx.author.send(content=STR_ENLIST_FAILED)

        else:
            await ctx.author.send(content=STR_NO_ACTIVE_WAR)

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):
        try:
            data = ctx.data
            if 'custom_id' not in data:
                return
            id: str = data['custom_id']
            if id.startswith('btn:enlist:'):
                id = id[11:]
                war = None
                for w in self.state.wars:
                    w = self.state.wars[w]
                    if w.id == id:
                        war = w
                        break
            else:
                return

            if ctx.author in self.users_enlisting:
                proc = self.users_enlisting[ctx.author]
                if proc is not None:
                    proc.close()
                    print('Proc killed')
                del self.users_enlisting[ctx.author]

            self.users_enlisting[ctx.author] = self.do_enlist(war, ctx)
            await self.users_enlisting[ctx.author]
        except:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())
