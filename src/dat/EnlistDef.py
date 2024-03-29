import discord

from utils.details import replace_emojis, replace_weapons_abbrev

import re

weapon_abrev_regex = re.compile(r'( ?\([0-9]*\))')


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
        self.roster[entry.username] = entry

    def as_dict(self):
        result = {}
        for entry in self.roster:
            result[entry] = self.roster[entry].__dict__()
        return result

    def from_dict(self, data):
        self.roster = {}
        for key in data:
            self.roster[key] = Enlistment(**data[key])
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

    def __init__(self, disc_name=None, username=None, level=None,
                 faction=None, company=None, group=None, roles=None,
                 edit_key=None,
                 **args):
        self.disc_name = disc_name
        self.username = username
        self.faction = faction
        self.company = company
        self.edit_key = edit_key

        try:
            self.level = int(level)
        except:
            self.level = -1

        self.group = group

        self.roles: dict = roles
        if roles is None:
            self.roles = {}

        # if data is not None:
        #     self.from_dict(data)

    def copy(self):
        return Enlistment(username=self.username,
                          disc_name=self.disc_name,
                          level=self.level,
                          faction=self.faction,
                          company=self.company,
                          roles=self.roles,
                          group=self.group,
                          edit_key=self.edit_key)

    def __dict__(self):
        return {
            'username': self.username,
            'disc_name': self.disc_name,
            'level': self.level,
            'faction': self.faction,
            'company': self.company,
            'roles': self.roles,
            'group': self.group,
            'edit_key': self.edit_key
        }

    def data(self):
        role = None
        weapons = None
        for r in self.roles:
            role = r
            weapons = self.roles[r]
        weapons = weapons.split('/')
        return [
            self.username,
            self.level,
            role,
            weapons[0],
            weapons[1],
            self.group,
            self.company,
            self.faction
        ]

    def table_data(self) -> dict:
        role = None
        weapons = None
        for r in self.roles:
            role = r
            weapons = self.roles[r]
        weapons = weapons.split('/')
        data = {
            'username': self.username,
            'discord': self.disc_name,
            'faction': self.faction,
            'company': self.company,
            'level': max(0, min(self.level, 1000)),
            'role': role,
            'weapon1': weapons[0],
            'weapon2': weapons[1],
            'extra': self.group,
            'edit_key': self.edit_key,
        }
        # data2 = {}
        # for key in data:
        #     if data[key] is not None:
        #         data2[key] = data[key]
        return data

    def embed(self, state=None):
        embed = discord.Embed(title='War Enlistment')
        user_data = f'*Name*: {self.username} (level {self.level})\n*Faction*: {self.faction}\n*Company*: {self.company}'

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
        if self.group is not None:
            embed.add_field(name='Extra Information', value=self.group, inline=False)

        if state is not None:
            enlisted_wars = ''
            for war in state.wars:
                war = state.wars[war]
                if war.active and self.username in war.roster:
                    enlisted_wars += f'> {war.name}\n'
            if len(enlisted_wars) > 0:
                embed.add_field(name='Wars', value=enlisted_wars, inline=False)

        return embed

    def make_table_row(self):

        roles = ''
        weapons = ''
        for role in self.roles:
            roles = role
            weapons = self.roles[role]
            # roles += f'{role} ({self.roles[role]})\n'
        # roles = roles[:-1]

        company = f'({self.faction[0]}) {self.company}'
        name = f'[{self.level}] {self.username}'
        return [name, roles, weapons, company]
        # return f'\"{self.username}\", \"{self.level}\", \"{self.faction}\", \"{self.company}\", \"{roles}\"\n'

    def __str__(self):
        roles = ''
        weapons = ''
        for role in self.roles:
            roles = role
            weapons = self.roles[role]

        # return f'[{replace_emojis(roles)} {self.level}] **{self.username}** *[{self.company} ({self.faction[0]})]*'
        weapons = replace_weapons_abbrev(weapons)
        matches = weapon_abrev_regex.findall(weapons)
        for m in matches:
            weapons = weapons.replace(m, '')
        return f'{self.level} {replace_emojis(roles)} **{self.username}** *[{weapons}]*'
        # return f'*{self.username}* *[{weapons}]*'

    def roster_line(self, abrv_line):
        if not abrv_line:
            roles = ''
            weapons = ''
            for role in self.roles:
                roles = role
                weapons = self.roles[role]
            return f'{self.level} {replace_emojis(roles)} **{self.username}** *[{weapons}]*'

        else:
            roles = ''
            weapons = ''
            for role in self.roles:
                roles = role
                weapons = self.roles[role]

            # return f'[{replace_emojis(roles)} {self.level}] **{self.username}** *[{self.company} ({self.faction[0]})]*'
            weapons = replace_weapons_abbrev(weapons)
            matches = weapon_abrev_regex.findall(weapons)
            for m in matches:
                weapons = weapons.replace(m, '')
            # return f'{self.level} {replace_emojis(roles)} **{self.username}** *[{weapons}]*'
            return f'{self.username} *[{weapons}]*'

    def sort_key(self):

        r = ''
        for role in self.roles:
            r = role
        return r + str(self.level) + str(self.company)

    async def send_message(self, client: discord.Client, content=None, embed=None):
        for guild in client.guilds:
            user = guild.get_member_named(self.disc_name)
            if user is not None:
                try:
                    await user.send(content=content, embed=embed)
                except:
                    pass
                return
