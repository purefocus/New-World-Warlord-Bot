from discord.ext import commands, tasks
import discord
from bot_state import *
from forms.create_war import *
from forms.enlist_form import cmd_enlist
from forms.war_management import *
from forms.bot_configure import *
from utils.botutil import *
from cogs.cog_enlistment import *
from cogs.cog_management import WarManagementCog
from cogs.cog_admin import AdminCog
from cogs.cog_extras import ExtrasCog
from cogs.cog_worldstatus import WorldStatusCog
from cogs.cog_verification import VerificationCog

intents = discord.Intents.all()

client = commands.Bot(" ", intents=intents)

ui = UI(client, slash_options={'auto_sync': False, "wait_sync": 2, "delete_unused": False})
config = Config()
config.load()
state = BotState(client, config)
state.load_war_data()

client.add_cog(WarManagementCog(client, state))
client.add_cog(DMEnlistmentCog(client, state))
client.add_cog(AdminCog(client, state, ui))
client.add_cog(ExtrasCog(client, state))
client.add_cog(WorldStatusCog(client, state))

client.add_cog(VerificationCog(client, state))


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

# @ui.slash.command(options=[
#     SlashOption(str, name='attacking', description='Who is attacking? <faction> (<company>)', required=True),
#     SlashOption(str, name='defending', description='Who is Defending? <faction> (<company>)', required=True),
#     SlashOption(str, name='location', description='Where is this war?', required=True),
#     SlashOption(str, name='time', description='When is the war going to be held?', required=True),
#     SlashOption(str, name='owner', description='What company is running this war?', required=True),
# ], description='Creates a new instance for a war that can be signed up for.', **cmd_cfg_elev)
# async def create_war(ctx, attacking, defending, location, time, owner):
#     await cmd_create_war(ctx, attacking, defending, location, time, owner, state)


@ui.slash.command(description='Flags a war as ended, disabling the ability to sign up for it', **cmd_cfg_mod)
async def end_war(ctx):
    user: discord.User = ctx.author
    await cmd_end_war(state, ctx)


@ui.slash.command(description='Reposts the war notification', **cmd_cfg_elev)
async def repost_war(ctx):
    await cmd_repost_war(state, ctx)


@ui.slash.command(description='posts a war notification in your current channel', **cmd_cfg_elev)
async def post_war(ctx):
    await cmd_post_war(state, ctx)


@ui.slash.command(description='posts a war enlistment button in your current channel', **cmd_cfg_elev)
async def post_enlist(ctx):
    await cmd_post_btn(state, ctx)


@ui.slash.command(description='Replies with a table of all the users enlisted for a specific war',
                  **cmd_cfg_elev)
async def get_enlisted(ctx):
    await cmd_get_enlisted(state, ctx)


@ui.slash.command(
    description='Generates a CSV file with a table of everyone who signed up (Can be imported into excel).',
    **cmd_cfg_elev)
async def download_enlisted(ctx):
    await cmd_dl_enlisted(state, ctx)


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

@ui.slash.command(name='warlord_cfg', options=[
    SlashOption(str, name='options', description='configuration options', required=True),
], description='Allows configuring the bot', **cmd_cfg_mod)
async def warlord_config(ctx, options: str):
    await cmd_bot_configure(state, ctx, options)


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

        # await ui.slash.sync_commands(delete_unused=True)

        # await state.update_presence()
        for war in state.wars:
            war = state.wars[war]
            if war.active:
                await state.update_war_boards(war)
        # guild: discord.Guild = client.get_guild(894675526776676382)

        # user_map = state.users.users
        # new_users = UserData()
        # for user in guild.members:
        #     if user.display_name.lower() in user_map:
        #         new_users.add_user(str(user), user_map[user.display_name.lower()])
        # new_users.save('../../files/user_data.json')

    except Exception as e:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())


state.load_war_data()

client.run(config.bot_token)

if __name__ == '__main__':
    pass
