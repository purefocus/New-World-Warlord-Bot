import json

import config as cfg
from dat.EnlistDef import Enlistment
from utils.google_forms import post_enlistment


class User:

    def __init__(self):
        pass


class UserData:
    def __init__(self):
        self.users = {}
        self.name_to_disc_map = {}

    def add_user(self, disc_name, user: Enlistment):
        if disc_name in self.users:
            u = self.users[disc_name]
            user.edit_key = u.edit_key
        self.users[disc_name] = user
        self.name_to_disc_map[user.username] = disc_name
        post_enlistment(user)

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
                self.name_to_disc_map[enl.username.lower()] = enl.disc_name
                if enl.edit_key is None:
                    post_enlistment(enl)
                    need_update = True
            # print_dict(self.name_to_disc_map)
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
        try:
            if '#' not in name:
                name = self.name_to_disc_map[name.lower()]
            if name in self.users:
                return self.users[name]
        except:
            pass
        return None

    def __contains__(self, item):
        if isinstance(item, str):
            if '#' not in item:
                item = self.name_to_disc_map[item.lower()]
            return item.lower() in self.users
        return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Enlisted: {len(self.users)}'
