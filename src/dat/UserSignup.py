import discord
from dat.EnlistDef import Enlistment


class SignupList:

    def __init__(self, data=None):
        self.roster = {}

        if data is not None:
            self.from_dict(data)

    def is_enlisted(self, name):
        if isinstance(name, UserSignup):
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
            self.roster[key] = UserSignup(**data[key])
        return self

    def __getitem__(self, item):
        if item in self.roster:
            return self.roster[item]
        return None

    def __len__(self):
        return len(self.roster)

    def __iter__(self):
        return self.roster.__iter__()


class UserSignup:

    def __init__(self, username=None, faction=None, company=None, level=None,
                 role=None, primary_weapon=None, secondary_weapon=None, preferred_group=None):
        self.username = username
        self.faction = faction
        self.company = company
        self.level = level
        self.role = role
        self.primary_weapon = primary_weapon
        self.secondary_weapon = secondary_weapon
        self.preferred_group = preferred_group

    def as_dict(self):
        return {
            'username': self.username,
            'faction': self.faction,
            'company': self.company,
            'level': self.level,
            'role': self.role,
            'primary_weapon': self.primary_weapon,
            'secondary_weapon': self.secondary_weapon,
            'preferred_group': self.preferred_group
        }

    def from_dict(self, data):
        self.username = data['username']
        self.faction = data['faction']
        self.company = data['company']
        self.level = data['level']
        self.role = data['role']
        self.primary_weapon = data['primary_weapon']
        self.secondary_weapon = data['secondary_weapon']
        self.preferred_group = data['preferred_group']

    def embed(self) -> discord.Embed:
        embed = discord.Embed(title='War Enlistment')
        user_data = f'*name*: {self.username} (level {self.level})\n*Faction*: {self.faction}\n*Company*: {self.company}'

        embed.add_field(name='User', value=user_data, inline=False)

        embed.add_field(name='Role', value=self.role, inline=True)
        embed.add_field(name='Weapons', value=f'{self.primary_weapon}\n{self.secondary_weapon}', inline=True)
        if self.preferred_group is None or len(self.preferred_group) == 0:
            self.preferred_group = 'None'
        embed.add_field(name='Preferred Group', value=self.preferred_group, inline=False)

        return embed

    def to_enlistment(self):
        en = Enlistment()
        en.username = self.username
        en.faction = self.faction
        en.company = self.company
        en.roles[self.role] = f'{self.primary_weapon}/{self.secondary_weapon}'
        en.level = self.level

        return en
