import discord


class Enlisted:

    def __init__(self, data=None):
        self.roster = {}

        if data is not None:
            self.from_dict(data)

    def is_enlisted(self, name):
        if isinstance(name, Enlistment):
            return name.username if name.username in self.roster else None

        return name if name in self.roster else None

    def enlist(self, entry):
        if entry.id is None:
            entry.id = str(len(self.roster))
        self.roster[entry.username] = entry

    def as_dict(self):
        result = {}
        for entry in self.roster:
            result[entry] = self.roster[entry].as_dict()
        return result

    def from_dict(self, data):
        self.roster = {}
        for key in data:
            self.roster[key] = Enlistment(data[key])
        return self

    def __getitem__(self, item):
        if item in self.roster:
            return self.roster[item]
        return None

    def __len__(self):
        return len(self.roster)

    def __iter__(self):
        return self.roster.__iter__()

    def get_embeded(self):
        embed = discord.Embed(title='War Enlistments')


class Enlistment:

    def __init__(self, data=None):
        self.id = None
        self.username = None
        self.level = None
        self.faction = None
        self.company = None

        self.group = None

        self.roles: dict = {}

        if data is not None:
            self.from_dict(data)

    def copy(self):
        cpy = Enlistment()
        cpy.username = self.username
        cpy.level = self.level
        cpy.faction = self.faction
        cpy.company = self.company
        cpy.roles = self.roles.copy()

        return cpy

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'level': self.level,
            'faction': self.faction,
            'company': self.company,
            'roles': self.roles,
            'group': self.group
        }

    def from_dict(self, dic):
        self.id = dic['id']
        self.username = dic['username']
        self.level = dic['level']
        self.faction = dic['faction']
        self.company = dic['company']
        self.roles = dic['roles']
        self.group = dic['group']
        return self

    def create_embed(self):
        embed = discord.Embed(title='War Enlistment')
        user_data = f'*name*: {self.username} (level {self.level})\n*Faction*: {self.faction}\n*Company*: {self.company}'

        embed.add_field(name='User', value=user_data, inline=False)

        if len(self.roles) == 0:
            roles = '---'
            weapons = '---'
        else:
            roles = ''
            weapons = ''
            for key in self.roles:
                roles += f'{key}\n'
                weapons += f'{self.roles[key]}\n'

        embed.add_field(name='Roles', value=roles, inline=True)
        embed.add_field(name='Weapons', value=weapons, inline=True)

        return embed

    def make_table_row(self):

        roles = ''
        weapons = ''
        for role in self.roles:
            roles = role
            weapons = self.roles[role]
            # roles += f'{role} ({self.roles[role]})\n'
        # roles = roles[:-1]

        return [self.username, self.level, self.faction, self.company, roles, weapons]
        # return f'\"{self.username}\", \"{self.level}\", \"{self.faction}\", \"{self.company}\", \"{roles}\"\n'
