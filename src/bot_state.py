from dat.WarDef import *
import config
import json
import discord
from discord.ext import commands
from discord_ui import Button


class BotState:

    def __init__(self, client, config):
        self.client: commands.Bot = client
        self.wars = {}
        self.config = config

        self.war_selection = {}

    async def add_enlistment(self, war: WarDef, user: Enlistment, save=True, announce=True):
        try:
            num_enlisted = len(war)
            if isinstance(user, UserSignup):
                enl = user.to_enlistment()
                war.add_enlistment(enl)
            else:
                war.add_enlistment(user)

            if self.config.announce_signup and announce:
                await self.announce_signup(user)

            if num_enlisted != len(war):
                await self.update_war_boards(war)

            if save:
                self.save_war_data()

        except Exception as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    async def announce_signup(self, user):
        if self.config.announce_signup:
            for ch in self.config.get_signup_channels():
                await ch.send(embed=user.embed())

    def add_war(self, war: WarDef):
        if war.location in self.wars:
            old_war = self.wars[war.location]
            if war.owners == old_war.owners \
                    or war.war_time == old_war.war_time \
                    or war.attacking == old_war.attacking \
                    or war.defending == old_war.defending:
                war.enlisted = old_war.enlisted
                war.war_board = old_war.war_board
                war.groups = old_war.groups
                war.id = old_war.id

        self.wars[war.location] = war

    def save_war_data(self):
        saved_data = {}
        for w in self.wars:
            saved_data[w] = self.wars[w].as_dict()

        json.dump(saved_data, open(config.WAR_DATA, 'w+'), indent=4)

        # print('Saved: ', saved_data)

    def load_war_data(self):
        try:
            war_data = json.load(open(config.WAR_DATA, 'r+'))

            for w in war_data:
                self.add_war(WarDef(war_data[w]))

        except Exception as e:
            self.wars = {}
            raise e

    def get_modifying_war(self, userid):
        if userid in self.war_selection:
            return self.war_selection[userid]
        else:
            return None

    def set_modifying_war(self, userid, war):
        self.war_selection[userid] = war

    async def update_war_boards(self, war):
        for guild in self.client.guilds:
            if str(guild.id) in war.war_board:
                dat = war.war_board[str(guild.id)]
                channel = guild.get_channel(int(dat['cid']))
                msg = channel.get_partial_message(int(dat['mid']))
                if msg is not None:
                    await msg.edit(**self.create_board(war))

    def create_board(self, war: WarDef, btn=False):
        ret = {
            'embed': war.embeds(),
        }
        if btn:
            ret['components'] = [
                Button(custom_id=f'btn:enlist:{war.location}', label='Enlist Now!')
            ]
        return ret

    async def add_war_board(self, war: WarDef, update_if_exists=True):
        if war is not None:
            channels = self.config.get_notice_channels()
            for ch in channels:
                flag = True
                if str(ch.guild.id) in war.war_board:
                    dat = war.war_board[str(ch.guild.id)]
                    if int(ch.id) == int(dat['cid']):
                        msg = ch.get_partial_message(int(dat['mid']))
                        if msg is not None:
                            if update_if_exists:
                                await msg.edit(**self.create_board(war))
                                flag = False
                            else:
                                await msg.delete()

                if flag:
                    msg: discord.Message = await ch.send(**self.create_board(war, btn=True))
                    war.add_board(msg)
