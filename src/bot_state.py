from dat.WarDef import *
import json


class BotState:

    def __init__(self, client, config):
        self.client = client
        self.wars = {}
        self.config = config

        self.war_selection = {}

    def add_war(self, war: WarDef):
        self.wars[war.location] = war

    def save_war_data(self):
        saved_data = {}
        for w in self.wars:
            saved_data[w] = self.wars[w].as_dict()

        json.dump(saved_data, open('wardata.json', 'w'), indent=4)

        print('Saved: ', saved_data)

    def load_war_data(self):
        try:
            war_data = json.load(open('wardata.json', 'r'))

            for w in war_data:
                self.add_war(WarDef(war_data[w]))

        except Exception as e:
            raise e
            self.wars = {}

    def get_modifying_war(self, userid):
        if userid in self.war_selection:
            return self.war_selection[userid]
        else:
            return None

    def set_modifying_war(self, userid, war):
        self.war_selection[userid] = war
