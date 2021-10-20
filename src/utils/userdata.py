import json
from dat.EnlistDef import Enlistment
import config as cfg

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
        pass

    def save(self):
        pass

    def __getitem__(self, name):
        return self.users[name.lower()]

    def __contains__(self, item):
        if isinstance(item, str):
            return item.lower() in self.users
