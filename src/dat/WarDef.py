import discord
from dat.UserSignup import *
from dat.EnlistDef import *
from dat.GroupAssignments import *

from utils.data import *

import uuid


class WarDef:

    def __init__(self, data=None):
        self.id = str(uuid.uuid4())

        self.name = None
        self.active = False

        self.attacking = None
        self.defending = None

        self.location = None
        self.war_time = None
        self.owners = None
        self.enlisted = Enlisted()
        self.roster = []
        # self.war_board = []
        self.boards = []

        self.looking_for = None

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
            'enlisted': self.enlisted.as_dict(),
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
        self.enlisted = Enlisted(dic['enlisted'])
        if 'name' in dic:
            self.name = dic['location']#dic['name']
        if 'roster' in dic:
            self.roster = dic['roster']

        self.boards = parse_message_references(dic['boards'])

        if 'looking_for' in dic:
            self.looking_for = dic['looking_for']

        self.groups.from_dict(dic['groups'])

        return self

    def add_board(self, msg: discord.Message):
        self.boards.append(MessageReference(msg=msg))
        # self.war_board[str(msg.guild.id)] = {'cid': msg.channel.id, 'mid': msg.id}

    def add_enlistment(self, enlisted) -> bool:
        name = self.enlisted.is_enlisted(enlisted)
        self.enlisted.enlist(enlisted)
        if enlisted.username not in self.roster:
            self.roster.append(enlisted.username)

        return name is not None

    def get_embeded(self):
        embed = discord.Embed(title=f':exclamation: __War Signup!__ :exclamation: ')
        # embed.set_author(name='Test')
        if self.attacking is not None:
            embed.add_field(name='Details',
                            value=f'Location: `{self.location}`\nTime: `{self.war_time}`\nContact: {self.owners}',
                            inline=False)
            embed.add_field(name='Attackers', value=self.attacking, inline=True)
            embed.add_field(name='Defenders', value=self.defending, inline=True)

            self.groups.embed(embed)

        embed.add_field(name='Enlisted',
                        value=f'{str(len(self.roster))}',
                        inline=False)

        if self.looking_for is not None:
            embed.add_field(name='Looking for', value=self.looking_for)

        embed.set_footer(text='Use /enlist to sign up!')

        # embed.set_footer(text=f'\nID: {self.id}')

        return embed

    def __len__(self):
        return len(self.enlisted)

    def __repr__(self):
        return f'{self.location}'

    def create_table(self, users, filter=None):

        table = []

        for enlisted in self.roster:
            entry = users[enlisted]
            if filter is None or filter(entry):
                table.append(entry)

        return table

    def embeds(self):
        # ret = [self.get_embeded(), self.groups.embed()]
        # if self.groups is not None and len(self.groups) > 0:
        #     ret.append(self.groups.embed())
        return self.get_embeded()
