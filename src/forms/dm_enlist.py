import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

from discord_ui import *

from utils.colorprint import *
from utils.details import WAR_ROLES, WEAPON_CHOICES, FACTIONS

from dat.UserSignup import UserSignup

from views.view_confirm import ask_confirm

import asyncio

question_list = [
    {
        'question': 'What is your character name?',
        'response_type': str,
        'key': 'name'
    },
    {
        'question': 'What level is your character?',
        'response_type': int,
        'key': 'level',
        'check': lambda response, answers: None if 0 < response <= 60 else 'Your answer must be between 0-60'
    },
    {
        'question': 'What Faction are you?',
        'choices': FACTIONS,
        'key': 'faction'
    },
    {
        'question': 'What Company are you in?',
        'response_type': str,
        'key': 'company'
    },
    {
        'question': 'What is your desired role?',
        'choices': WAR_ROLES,
        'key': 'role'
    },
    {
        'question': 'What is your Primary Weapon?',
        'choices': WEAPON_CHOICES,
        'key': 'primary_weapon'
    },
    {
        'followup': lambda x: f"What is your Mastery Level for your {x['primary_weapon']}",
        'response_type': int,
        'key': 'primary_level',
        'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    },
    {
        'question': 'What is your Secondary Weapon?',
        'choices': WEAPON_CHOICES,
        'key': 'secondary_weapon',
        'check': lambda response, answers: None if response != answers[
            'primary_weapon'] else 'You must select a different weapon from your primary!'
    },
    {
        'followup': lambda x: f"What is your Mastery Level for your {x['secondary_weapon']}",
        'response_type': int,
        'key': 'secondary_level',
        'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    },
    {
        'question': 'Do you have a preferred group? Enter `None` if you do not have one.',
        'response_type': str,
        'key': 'group'
    },
]


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

    msg = await ctx.author.send(content=question, components=components)

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
            await ctx.author.send(
                f'Hello, you have chosen to enlist in the war for {war.location}\nPlease answer the following questions:\n')
            responses = {}
            for q in question_list:

                key, response = None, None
                while response is None:
                    key, response = await question(self.client, ctx, responses, **q)
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

            await self.state.add_enlistment(war, user.to_enlistment())

            return True

        except asyncio.TimeoutError as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())
        return False

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.client.user:
            return

        channel = msg.channel
        if channel.type != discord.ChannelType.private:
            return

    @commands.Cog.listener('on_interaction_received')
    async def on_interaction(self, ctx: Interaction):
        try:
            data = ctx.data
            id: str = data['custom_id']
            if id.startswith('btn:enlist:'):
                id = id[11:]
                war = None
                for w in self.state.wars:
                    w = self.state.wars[w]
                    if w.id == id:
                        war = w
                        break

                if ctx.author not in self.users_enlisting:
                    await ctx.respond(ninja_mode=True)
                    # war = self.state.wars[id]
                    if war is not None:
                        print('Enlistment Started!')
                        self.users_enlisting[ctx.author] = True

                        ask = True
                        if self.state.users.has_user(ctx.author.display_name):
                            ask = await ask_confirm(self.state, ctx,
                                                    'You have enlisted in a previous war! Would you like to update your information?')
                        if ask:
                            success = await self.enlist_questionair(war, ctx)
                        else:
                            success = True
                        del self.users_enlisting[ctx.author]
                        print('Enlistment Ended! ', len(self.users_enlisting))

                        if success:
                            await ctx.author.send(
                                content=f'You have successfully been enlisted for the war **{id}**\n'
                                        f'You can update you enlistment by clicking the \'Enlist Now!\' button again.')
                        else:
                            await ctx.author.send(
                                content=f'Something went wrong and you have not been enlisted.')

                    else:
                        await ctx.author.send(
                            content='Sorry, This war is no longer active!\nIf this is a mistake, please contact an admin!')
        except:
            pass
