from discord.ext import commands, tasks
import discord
from bot_state import *
from forms.create_war import *
from forms.enlist_form import cmd_enlist
from forms.war_management import *
from utils.botutil import *
from cogs import *
from utils.colorprint import print_color_table

from database.SqlDatabase import SqlDatabase

# fc = 0
# lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# for i in range(len(lst)):
#     print(lst[fc], end='')
#     if fc % 2 == 1:
#         print('c', end='\n')
#     fc += 1
# em = '▪️'
# print(em, len(em))
# em = em.encode('UTF-8')
# print(em, len(em))
#
# # test = '▪️ purefocus\'s Channel'
# # print(em in test)
#
# sys.exit(0)
# print_color_table()
intents = discord.Intents.all()

client = commands.Bot(" ", intents=intents)

ui = UI(client, slash_options={'auto_sync': False, "wait_sync": 2, "delete_unused": None})
ui.logger.setLevel(10)
ui.logger.disabled = False

config = Config()
config.load()
state = BotState(client, config)
state.load_war_data()
state.ui_client = ui

# database = SqlDatabase(config)
# # state.db = database
# users = database.users.get_users(username='f')
# print_dict(users)
# # for user in state.users.users:
# #     user = state.users.users[user]
# #     database.users.insert_user(user)
# # user = state.users.users['purefocus#3061']
# # database.users.insert_user(user)
# # #
# user = database.users.get_user('purefocus#3061')
# print_dict(user.__dict__)
# #
# sys.exit()
#
# from utils.google_forms import post_enlistment
#
# for user in state.users.users:
#     user: Enlistment = state.users.users[user]
#     post_enlistment(user)

state.cogs = {
    #
    'war_management': WarManagementCog(client, state),
    'dm_enlist': DMEnlistmentCog(client, state),
    'roster': RosterCog(client, state),
    'war_groups': WarGroupsCog(client, state),

    'extras': ExtrasCog(client, state),
    'world_status': WorldStatusCog(client, state),
    #
    # 'admin': AdminCog(client, state, ui),
    # 'verify': VerificationCog(client, state),
    # 'dm_verify': DMVerificationCog(client, state),
    'config': ConfigurationCog(client, state),
    'bot_management': BotManagementCog(client, state, ui),
    #
    'temp_voice': TempVoiceCog(client, state),
    # 'war_voice': WarVoiceCog(client, state),
}
if config.guildcfg(894675526776676382) is not None:
    state.cogs['admin'] = AdminCog(client, state, ui)
    state.cogs['verify'] = VerificationCog(client, state)

for c in state.cogs:
    client.add_cog(state.cogs[c])


# # War Related Cogs
# client.add_cog(WarManagementCog(client, state))
# enl = DMEnlistmentCog(client, state)
# client.add_cog(enl)
# client.add_cog(RosterCog(client, state))
#
# # Utility Cogs
# client.add_cog(ExtrasCog(client, state))
# client.add_cog(WorldStatusCog(client, state))
#
# # Administrative Cogs
# client.add_cog(AdminCog(client, state, ui))
# client.add_cog(VerificationCog(client, state))
#
# enl.walk_commands()

####################
#  War Enlistment  #
####################

# @ui.slash.command(options=[
#     SlashOption(str, name='username', required=True),
#     SlashOption(int, name='level', required=True),
#     SlashOption(str, name='company', required=True),
# ], description='Enlists you to participate in a war! (Do not forget to sign up at the war table too!)',
#     **config.cmd_cfg)
# async def enlist(ctx, username, level, company):
#     await cmd_enlist(state, ctx, username, level, company)


####################
#   War Creation   #
####################

@ui.slash.command(options=[
    SlashOption(str, name='attacking', description='Who is attacking?', required=True),
    SlashOption(str, name='defending', description='Who is Defending?', required=True),
    SlashOption(str, name='location', description='Where is this war?', required=True),
    SlashOption(str, name='time', description='When is the war going to be held?', required=True),
    SlashOption(str, name='owner', description='What company is running this war?', required=True),
], description='Creates a new instance for a war that can be signed up for.', **cmd_cfg_elev)
async def create_war(ctx, attacking, defending, location, time, owner):
    await cmd_create_war(ctx, attacking, defending, location, time, owner, state)


#####################
#  Error Handling   #
#####################

@client.event
async def on_command_error(ctx, error):
    print(colors.red('[ERROR] Comand ', ctx.name, ': ', error))
    print_stack_trace()


@client.event
async def on_error(event_method, *args, **kwargs):
    print(colors.red('[ERROR] ', event_method, ': ', str(args), str(kwargs)))
    print_stack_trace()


#####################
# Bot Configuration #
#####################

# @ui.slash.command(name='warlord_cfg', options=[
#     SlashOption(str, name='options', description='configuration options', required=True),
# ], description='Allows configuring the bot', **cmd_cfg_mod)
# async def warlord_config(ctx, options: str):
#     await cmd_bot_configure(state, ctx, options)


####################
#    Bot Events    #
####################

@client.event
async def on_ready():
    try:
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')
        config.resolve(client)

        # for guild in client.guilds:
        #     print('Guild: ', guild.name)
        #     if guild.id == 782026589927637014:
        #         for ch in guild.channels:
        #             print('Actual Apes Channel: ', ch.name)

        for war in state.wars:
            war = state.wars[war]
            if war.active:
                await state.update_war_boards(war)

        for user in state.users.users:
            usr: Enlistment = state.users.users[user]
            if user != usr.disc_name:
                print(f'key and name do not match! {user} :: {usr.disc_name}')
            # for guild in client.guilds:
            #     for member in guild.members:
            #         if str(member).lower() == user:

        # await ui.slash.sync_commands()
    except Exception as e:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())


# state.load_war_data()

client.run(config.bot_token)

if __name__ == '__main__':
    pass
