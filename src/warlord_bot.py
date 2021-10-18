from discord.ext import commands

from bot_state import *
from forms.create_war import *
from forms.enlist_form import cmd_enlist
from forms.war_management import *
from forms.bot_configure import *
from utils.botutil import *
from forms.dm_enlist import *
from cog_management import WarManagementCog
from cog_admin import AdminCog

client = commands.Bot(" ")
ui = UI(client, slash_options={'auto_sync': True, "wait_sync": 2, "delete_unused": True})
config = Config()
config.load()
state = BotState(client, config)


####################
#  War Enlistment  #
####################

@ui.slash.command(options=[
    SlashOption(str, name='username', required=True),
    SlashOption(int, name='level', required=True),
    SlashOption(str, name='company', required=True),
], description='Enlists you to participate in a war! (Do not forget to sign up at the war table too!)',
    **config.cmd_cfg)
async def enlist(ctx, username, level, company):
    await cmd_enlist(state, ctx, username, level, company)


####################
#   War Creation   #
####################

@ui.slash.command(options=[
    SlashOption(str, name='attacking', description='Who is attacking? <faction> (<company>)', required=True),
    SlashOption(str, name='defending', description='Who is Defending? <faction> (<company>)', required=True),
    SlashOption(str, name='location', description='Where is this war?', required=True),
    SlashOption(str, name='time', description='When is the war going to be held?', required=True),
    SlashOption(str, name='owner', description='What company is running this war?', required=True),
], description='Creates a new instance for a war that can be signed up for.', **config.cmd_cfg_elev)
async def create_war(ctx, attacking, defending, location, time, owner):
    await cmd_create_war(ctx, attacking, defending, location, time, owner, state)


@ui.slash.command(description='Flags a war as ended, disabling the ability to sign up for it', **config.cmd_cfg_elev)
async def end_war(ctx):
    await cmd_end_war(state, ctx)


@ui.slash.command(description='Reposts the war notification', **config.cmd_cfg_elev)
async def repost_war(ctx):
    await cmd_repost_war(state, ctx)


'''

####################
# War Organization #
####################

# @ui.slash.command(description='Creates 10 placeholder groups that for a war to place selected players in',
#                   **config.cmd_cfg_elev)
# async def make_groups(ctx):
#     await cmd_war_make_groups(state, ctx)
# 
# 
# @ui.slash.command(description='Changes which war you are focusing on.', **config.cmd_cfg_elev)
# async def select(ctx):
#     await cmd_war_select(state, ctx)
# 
# 
# @ui.slash.command(options=[
#     SlashOption(int, name='user_id', description='The ID of the user you are assigning a group', required=True),
#     SlashOption(int, name='group_id', description='The group you are assigning the user to. values: [0-9]',
#                 required=True),
#     SlashOption(str, name='role', description=f'{WAR_ROLES}', required=True),
# ], description='Assigns a player to a group', **config.cmd_cfg_elev)
# async def assign(ctx, user_id, group_id, role):
#     await cmd_war_assign(state, ctx, user_id, group_id, role)
# 
# 
# @ui.slash.command(options=[
#     SlashOption(int, name='user_id', description='The ID of the user you are removing from the war', required=True),
# ], description='Unassigns a player from all groups', **config.cmd_cfg_elev)
# async def unassign(ctx, user_id):
#     await cmd_war_unassign(state, ctx, user_id)
# 
# 
# @ui.slash.command(options=[
#     SlashOption(int, name='group_id', description='The group you are configuring', required=True),
#     SlashOption(str, name='name', description='The name of the group', required=True),
# ], description='Renames a group. The group ID will remain the same though [0-10]', **config.cmd_cfg_elev)
# async def group_configure(ctx, group_id, name):
#     await cmd_war_group_configure(state, ctx, group_id, name)

'''


@ui.slash.command(description='Replies with a table of all the users enlisted for a specific war',
                  **config.cmd_cfg_elev)
async def get_enlisted(ctx):
    await cmd_get_enlisted(state, ctx)


@ui.slash.command(
    description='Generates a CSV file with a table of everyone who signed up (Can be imported into excel).',
    **config.cmd_cfg_elev)
async def download_enlisted(ctx):
    await cmd_dl_enlisted(state, ctx)


#####################
#  Error Handling   #
#####################

@client.event
async def on_command_error(ctx, error):
    print(colors.red('[ERROR] Comand ', ctx.name, ': ', error))
    import traceback
    import sys
    traceback.print_exception(*sys.exc_info())


@client.event
async def on_error(event_method, *args, **kwargs):
    print(colors.red('[ERROR] ', event_method, ': ', str(args), str(kwargs)))
    import traceback
    import sys
    traceback.print_exception(*sys.exc_info())


#####################
# Bot Configuration #
#####################

@ui.slash.command(name='warlord_cfg', options=[
    SlashOption(str, name='options', description='configuration options', required=True),
], description='Allows configuring the bot', **config.cmd_cfg_elev)
async def warlord_config(ctx, options: str):
    await cmd_bot_configure(state, ctx, options)


@ui.slash.command(name='warlord_cmd_sync', **config.cmd_cfg_elev)
async def warlord_cmd_sync(ctx):
    await ui.slash.sync_commands(delete_unused=True)


# @ui.slash.command(description='Shutdown the bot', **config.cmd_cfg_elev)
# async def warlord_shutdown(ctx):
#     state.save_war_data()
#     config.save()
#     import sys
#     sys.exit(1)
#     # TODO: Elevate Permissions


####################
#    Bot Events    #
####################

# @client.event
# async def on_message(message: discord.Message):
#     try:
#         if message.author == client.user:
#             return
#
#         if state.config.is_war_management(message):
#             await handle_management_message(state, message)
#
#         if state.config.is_war_signup(message):
#             await handle_signup_message(state, message)
#     except Exception as e:
#         import traceback
#         import sys
#         traceback.print_exception(*sys.exc_info())

@client.event
async def on_ready():
    try:
        print(f'Logged in as {client.user} (ID: {client.user.id})')
        print('------')
        config.resolve(client)

        # await config.test_resolved()

        state.load_war_data()
        for war in state.wars:
            await update_war_boards(state.wars[war], state)

    except Exception as e:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())


state.load_war_data()
for war in state.wars:
    generate_enlistment_pdf(state.wars[war])

client.add_cog(WarManagementCog(client, state))
client.add_cog(DMEnlistmentCog(client, state))
client.add_cog(AdminCog(client, state))
client.run(config.bot_token)

if __name__ == '__main__':
    pass
