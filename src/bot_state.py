from dat.WarDef import *
import config
import json
import discord
from discord.ext import commands


class BotState:

    def __init__(self, client, config):
        self.client: commands.Bot = client
        self.wars = {}
        self.config = config

        self.war_selection = {}

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

        print('Saved: ', saved_data)

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
