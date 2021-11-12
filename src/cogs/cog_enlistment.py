import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog, context_cog
from bot_state import BotState

from dat.datadef import *

from discord_ui import *

from utils.colorprint import *
from utils.details import WAR_ROLES, WEAPON_CHOICES, FACTIONS

from dat.UserSignup import UserSignup
from dat.UserProfile import UserProfile

from views.view_confirm import ask_confirm

import asyncio
import config as cfg
from utils.permissions import *

question_list = {
    'name': {
        'question': 'What is your character name?',
        'response_type': str,
    },
    'level': {
        'question': 'What level is your character? *(Use your average gear score if above level 60)*',
        'response_type': int,
        # 'check': lambda response, answers: None if 0 < response <= 600 else 'Your answer must be between 0-60'
    },
    # 'gearscore': {
    #     'question': 'What level is your Gear Score?',
    #     'response_type': int,
    #     'askif': lambda answers: answers['level'] == 60
    # },
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
    # 'primary_level': {
    #     'followup': lambda x: f"What is your Mastery Level for your {x['primary_weapon']}",
    #     'response_type': int,
    #     'check': lambda response, answers: None if 0 < response <= 20 else 'Your answer must be between 0-20'
    # },
    'secondary_weapon': {
        'question': 'What is your Secondary Weapon?',
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
        'question': 'Do you have a preferred group? Enter `None` if you do not have one.',
        'response_type': str,
    }
}
STR_ENLIST_FAILED = 'Something went wrong and you have not been enlisted.'
STR_NO_ACTIVE_WAR = 'Sorry, This war is no longer active!\nIf this is a mistake, please contact an admin!'
STR_ENLIST_SUCCESS = 'You have successfully been enlisted for the war **%s**\n ' \
                     'You can update you enlistment by clicking the \'Enlist Now!\' button again.\n' \
                     '**Do not forget to also sign up at the in-game war board!**'


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

    async def enlist_questionair(self, war, ctx, udata=None):
        try:
            gcfg = self.state.config.guildcfg(ctx.guild_id)
            if gcfg is None:
                return
            user = UserProfile(ctx.author, name_enforcement=gcfg.name_enforcement,
                               company_enforcement=gcfg.company_enforcement)

            responses = {}
            if user.username is not None:
                responses['name'] = user.username

                if user.company is not None:
                    responses['faction'] = 'Syndicate'
                    responses['company'] = user.company

            if udata is not None:
                user.username = responses['name'] = udata.username
                user.faction = responses['faction'] = udata.faction
                user.company = responses['company'] = udata.company

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
                        return False
                responses[key] = response

            print_dict(responses)
            user = UserSignup()
            user.faction = responses['faction']
            user.company = responses['company']
            user.role = responses['role']
            user.username = responses['name']
            user.level = responses['level']
            # if 'gearscore' in responses:
            #     user.level = responses['gearscore']

            user.primary_weapon = f"{responses['primary_weapon']}"  # ({responses['primary_level']})"
            user.secondary_weapon = f"{responses['secondary_weapon']}"  # ({responses['secondary_level']})"
            pref_group = responses['group']
            if pref_group is not None and pref_group.lower() == 'none':
                pref_group = None
            user.preferred_group = pref_group

            return user

        except asyncio.TimeoutError as e:
            # import traceback
            # import sys
            # traceback.print_exception(*sys.exc_info())

            print(colors.red(f'Failed to enlist {ctx.author.display_name}!'))
            print(colors.red(f'\t-> {str(e)}'))

        return None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.client.user:
            return

        channel = msg.channel
        if channel.type != discord.ChannelType.private:
            return

    async def do_enlist(self, war: WarDef, ctx: Interaction):
        user = ctx.author
        # war = self.state.wars[id]
        if war is not None:
            print('Enlistment Started! ', str(ctx.author))
            # self.users_enlisting[ctx.author] = True

            msg = None
            ask = True
            udata = self.state.users[str(ctx.author)]
            if udata is not None:
                ask, msg = await ask_confirm(self.state, ctx,
                                             'You have enlisted in a previous war, so we can just reuse that information! '
                                             '\nWould you like to update your information instead? ',
                                             embed=udata.embed(), ret_msg=True,
                                             text=['Update Information', 'Enlist', "Cancel"],
                                             colors=['blurple', 'green', 'red'], cancel=True)
                if ask:
                    await msg.edit(content='**Please check your private messages!**', components=None, embed=None)
            if ask is None:
                await msg.edit(content='Enlistment Canceled', components=None, embed=None)
                return
            elif ask:

                if not ctx.responded:
                    try:
                        await ctx.respond(content='**Please check your private messages!**', hidden=True)
                    except:
                        pass
                correct = False
                while not correct:
                    try:
                        udata = await self.enlist_questionair(war, ctx, udata)
                    except:
                        break

                    if udata is not None:
                        correct = await ask_confirm(self.state, ctx.author, 'Is this information correct?',
                                                    embed=udata.embed(), hidden=False)

                    else:
                        break

                if not correct:
                    await ctx.author.send(content=STR_ENLIST_FAILED)

            # del self.users_enlisting[ctx.author]
            print('Enlistment Ended! ', str(ctx.author), len(self.users_enlisting))

            if udata is not None:
                await self.state.add_enlistment(str(ctx.author), war, udata, announce=ask)
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
        if not await check_permission(ctx, Perm.ENLIST):
            return
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
            try:
                del self.users_enlisting[ctx.author]
            except:
                pass
        except:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    @slash_cog(description='Enlist yourself to participate in wars!', **cfg.cmd_cfg)
    async def enlist(self, ctx: SlashedCommand):
        if not await check_permission(ctx, Perm.ENLIST):
            return
        try:
            war = self.state.wars['General Enlistment']

            if ctx.author in self.users_enlisting:
                proc = self.users_enlisting[ctx.author]
                if proc is not None:
                    proc.close()
                    print('Proc killed')
                del self.users_enlisting[ctx.author]

            self.users_enlisting[ctx.author] = self.do_enlist(war, ctx)
            await self.users_enlisting[ctx.author]
            try:
                del self.users_enlisting[ctx.author]
            except:
                pass
        except:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    @context_cog(type="user", name="Enlistment Lookup")
    async def enlistment_lookup(self, ctx, user: discord.Member):
        print('Enlistment Lookup! ', str(user))

        data = self.state.users[str(user)]
        if data is not None:
            await ctx.respond(content=' ', embed=data.embed(), hidden=True)
        else:
            await ctx.respond(content='No enlistment data found for this user!', hidden=True)
