from discord.ext import commands, tasks
import discord
from bot_state import *
from forms.create_war import *
from forms.enlist_form import cmd_enlist
from forms.war_management import *
from utils.botutil import *
from cogs import *

intents = discord.Intents.all()

client = commands.Bot(" ", intents=intents)

ui = UI(client, slash_options={'auto_sync': False, "wait_sync": 2, "delete_unused": None})
ui.logger.setLevel(10)
ui.logger.disabled = False
config = Config()
config.load()
state = BotState(client, config)
state.load_war_data()

cogs = [
    WarManagementCog(client, state),
    DMEnlistmentCog(client, state),
    RosterCog(client, state),

    ExtrasCog(client, state),
    WorldStatusCog(client, state),

    AdminCog(client, state, ui),
    VerificationCog(client, state),
    ConfigurationCog(client, state)
]

for cog in cogs:
    client.add_cog(cog)


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

        for war in state.wars:
            war = state.wars[war]
            if war.active:
                await state.update_war_boards(war)
        # await ui.slash.sync_commands()
    except Exception as e:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())


state.load_war_data()

client.run(config.bot_token)

if __name__ == '__main__':
    pass
