import json
from dat.EnlistDef import Enlistment
import config as cfg

from utils.google_forms import post_enlistment

import json

from utils.colorprint import *


class User:

    def __init__(self):
        pass


class UserData:
    def __init__(self):
        self.users = {}

    def add_user(self, disc_name, user: Enlistment):
        if disc_name in self.users:
            u = self.users[disc_name]
            user.edit_key = u.edit_key
        self.users[disc_name] = user
        # post_enlistment(user)


    def has_user(self, username: str):
        return username.lower() in self.users

    def load(self, file=None):
        try:
            if file is None:
                file = cfg.USER_DATA
            data = json.load(open(file, 'r'))
            need_update = False
            for key in data:
                entry: dict = data[key]
                entry['disc_name'] = key
                # print_dict(entry)
                enl = self.users[key] = Enlistment(**entry)
                if enl.edit_key is None:
                    post_enlistment(enl)
                    need_update = True
            if need_update:
                self.save()
        except Exception as e:
            print(e)

    def save(self, file=None):
        try:
            if file is None:
                file = cfg.USER_DATA
            data = {}
            for key in self.users:
                data[key] = self.users[key].__dict__()
            json.dump(data, open(file, 'w+'), indent=2)
        except Exception as e:
            print(e)

    def __getitem__(self, name) -> Enlistment:
        if name.lower() in self.users:
            return self.users[name.lower()]
        return None

    def __contains__(self, item):
        if isinstance(item, str):
            return item.lower() in self.users

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Enlisted: {len(self.users)}'
