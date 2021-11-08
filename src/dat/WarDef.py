import discord
from dat.UserSignup import *
from dat.EnlistDef import *
from dat.GroupAssignments import *

from utils.data import *

import uuid
from utils.details import WAR_ROLES

class WarDef:

    def __init__(self, data=None):
        self.id = str(uuid.uuid4())

        self.name = None
        self.active = False
        self.is_fake = False

        self.attacking = None
        self.defending = None

        self.location = None
        self.war_time = None
        self.owners = None
        # self.enlisted = Enlisted()
        self.roster = []
        # self.war_board = []
        self.boards = []

        self.looking_for = None
        self.additional_info = None

        self.groups = GroupAssignments(None, self)

        if data is not None:
            self.from_dict(data)

    def as_dict(self):
        ret = {
            'id': self.id,
            'name': self.name,
            'active': self.active,
            'attacking': self.attacking,
            'defending': self.defending,
            'location': self.location,
            'wartime': self.war_time,
            'owners': self.owners,
            'roster': self.roster,
            'additional': self.additional_info,
            # 'enlisted': self.enlisted.as_dict(),
            # 'boards': self.war_board,
            'boards': store_message_references(self.boards),
            'looking_for': self.looking_for,
            'groups': self.groups.__dict__()
        }
        return ret

    def from_dict(self, dic):
        self.id = dic['id']
        self.active = dic['active']
        self.attacking = dic['attacking']
        self.defending = dic['defending']
        self.location = dic['location']
        self.war_time = dic['wartime']
        self.owners = dic['owners']
        # self.war_board = dic['boards']
        # self.enlisted = Enlisted(dic['enlisted'])
        if 'name' in dic:
            self.name = dic['name']
        if 'roster' in dic:
            self.roster = dic['roster']
        if 'additional' in dic:
            self.additional_info = dic['additional']

        self.boards = parse_message_references(dic['boards'])

        if 'looking_for' in dic:
            self.looking_for = dic['looking_for']

        self.groups.from_dict(dic['groups'])

        return self

    def add_board(self, msg: discord.Message):
        self.boards.append(MessageReference(msg=msg))
        # self.war_board[str(msg.guild.id)] = {'cid': msg.channel.id, 'mid': msg.id}

    def add_enlistment(self, enlisted) -> bool:
        # name = self.enlisted.is_enlisted(enlisted)
        # self.enlisted.enlist(enlisted)
        if isinstance(enlisted, Enlistment):
            enlisted = enlisted.username

        if enlisted not in self.roster:
            self.roster.append(enlisted)
            return False

        return True

    def get_embeded(self):
        embed = discord.Embed(title=f':exclamation: __{self.location}!__ :exclamation: ')
        embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W_400x400.jpg')
        # embed.set_author(name='Test')
        if self.attacking is not None:
            embed.add_field(name='Details',
                            value=f'📆 {self.war_time}\n\n {self.owners} [link test](https://google.com/)',
                            inline=False)
            embed.add_field(name='Attackers', value=self.attacking, inline=True)
            embed.add_field(name='Defenders', value=self.defending, inline=True)

            # self.groups.embed(embed)

        if self.looking_for is not None:
            embed.add_field(name='Looking for', value=self.looking_for, inline=False)

        if self.additional_info is not None:
            info = self.additional_info
            if len(info) >= 1018:
                info = self.additional_info[:1018]
            embed.add_field(name='Additional Info', value=f'```{info}```', inline=False)

        embed.add_field(name='Enlisted',
                        value=f'{str(len(self.roster))}',
                        inline=False)

        # embed.set_footer(text='Use /enlist to sign up!')

        # embed.set_footer(text=f'\nID: {self.id}')

        return embed

    def __len__(self):
        return len(self.roster)

    def __repr__(self):
        return f'{self.location}'

    def make_description(self):
        if self.war_time is None:
            return f'Enlisted: {len(self.roster)}'
        return f'Enlisted: {len(self.roster)}  |  {self.war_time}'

    def create_table(self, users, filter=None):

        table = []

        for enlisted in self.roster:
            entry = users[enlisted]
            if entry is not None and (filter is None or filter(entry)):
                table.append(entry)

        return table

    def embeds(self):
        # ret = [self.get_embeded(), self.groups.embed()]
        # if self.groups is not None and len(self.groups) > 0:
        #     ret.append(self.groups.embed())
        return self.get_embeded()
