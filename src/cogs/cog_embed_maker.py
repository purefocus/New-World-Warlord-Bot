# from discord.ext import commands
# from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
#
# from utils.botutil import *
#
# from bot_state import *
# from utils.details import get_location, replace_weapon
#
# from views.view_confirm import ask_confirm
# from utils.colorprint import *
#
#
# class EmbedMakerCog(commands.Cog):
#
#     def __init__(self, client: commands.Bot, state: BotState):
#         self.client = client
#         self.state = state
#
#     @commands.Cog.listener()
#     async def on_message(self, msg: discord.Message):
#         await self.process_messages(msg, False)
#
#     @commands.Cog.listener()
#     async def on_message_edit(self, before: discord.Message, after: discord.Message):
#         await self.process_messages(after, True)
#
#     @commands.Cog.listener()
#     async def on_raw_message_edit(self, payload: discord.RawMessageUpdateEvent):
#         try:
#             if payload.cached_message is not None:
#                 return
#
#             data = payload.data
#             if 'author' not in data:
#                 return
#
#             if data['author']['id'] == str(self.client.user.id):
#                 return
#
#             mentions = data['mentions']
#             if mentions is not None:
#                 for mention in mentions:
#
#                     if mention['id'] == str(self.client.user.id):
#                         channel = self.client.get_channel(payload.channel_id)
#                         msg = await channel.fetch_message(payload.message_id)
#                         if msg is not None:
#                             await handle_management_message(self.state, msg, True)
#             # print_dict(payload.data)
#         except Exception as e:
#             import traceback
#             import sys
#             traceback.print_exception(*sys.exc_info())
