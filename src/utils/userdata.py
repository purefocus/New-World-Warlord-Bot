import json
from dat.EnlistDef import Enlistment
import config as cfg

import json


class User:

    def __init__(self):
        pass


class UserData:
    def __init__(self):
        self.users = {}

    def add_user(self, user: Enlistment):
        self.users[user.username.lower()] = user

    def has_user(self, username: str):
        return username.lower() in self.users

    def load(self):
        try:
            data = json.load(open(cfg.USER_DATA, 'r'))
            for key in data:
                entry: dict = data[key]
                self.users[key] = Enlistment(**entry)
        except Exception as e:
            print(e)

    def save(self):
        try:
            data = {}
            for key in self.users:
                data[key] = self.users[key].__dict__()
            json.dump(data, open(cfg.USER_DATA, 'w+'), indent=2)
        except Exception as e:
            print(e)

    def __getitem__(self, name) -> Enlistment:
        if name.lower() in self.users:
            return self.users[name.lower()]
        return None

    def __contains__(self, item):
        if isinstance(item, str):
            return item.lower() in self.users
