import discord
from dat.UserSignup import *
from dat.EnlistDef import *
from dat.GroupAssignments import *

from utils.data import *

import uuid
from utils.details import WAR_ROLES
from utils.details import parse_date

from database.tables.wars_table import WarRow
import datetime


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
        self.image_url = None
        # self.enlisted = Enlisted()
        self.roster = []
        self.absent = []
        # self.war_board = []
        self.boards = []

        self.looking_for = None
        self.additional_info = None
        self.private = None

        self.groups = GroupAssignments(None, self)

        if data is not None:
            self.from_dict(data)

    def make_war_row(self):
        row = WarRow()
        row.uuid = self.id
        row.owners = self.owners
        row.private = self.private or -1
        row.active = self.active
        row.name = self.name
        row.attacking = self.attacking
        row.defending = self.defending
        row.location = self.location
        row.created = datetime.datetime.now().timestamp()

        wartime = parse_date(self.war_time)
        if not isinstance(wartime, str):
            wartime = wartime.strftime('%Y-%m-%d %H:%M:%S')

        row.wartime = wartime
        row.image = self.image_url
        row.extra = self.additional_info

        return row

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
            'absent': self.absent,
            'private': self.private,
            'image_url': self.image_url,
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
        if 'image_url' in dic:
            self.image_url = dic['image_url']
        # self.war_board = dic['boards']
        # self.enlisted = Enlisted(dic['enlisted'])
        if 'name' in dic:
            self.name = dic['name']
        if 'roster' in dic:
            self.roster = dic['roster']
        if 'absent' in dic:
            self.absent = dic['absent']
        if 'additional' in dic:
            self.additional_info = dic['additional']
        if 'private' in dic:
            self.private = dic['private']

        self.boards = parse_message_references(dic['boards'])

        if 'looking_for' in dic:
            self.looking_for = dic['looking_for']

        self.groups.from_dict(dic['groups'])

        return self

    def can_post(self, ctx):
        return self.private is None or self.private == ctx.guild.id

    def add_board(self, msg: discord.Message):
        self.boards.append(MessageReference(msg=msg))
        # self.war_board[str(msg.guild.id)] = {'cid': msg.channel.id, 'mid': msg.id}

    def add_enlistment(self, enlisted) -> bool:
        # name = self.enlisted.is_enlisted(enlisted)
        # self.enlisted.enlist(enlisted)
        try:
            enlisted = enlisted.username
        except:
            pass

        if enlisted in self.absent:
            self.absent.remove(enlisted)

        if enlisted not in self.roster:
            self.roster.append(enlisted)
            return False

        return True

    def add_absent(self, enlisted) -> bool:
        try:
            enlisted = enlisted.username
        except:
            pass

        if enlisted in self.roster:
            self.roster.remove(enlisted)

        if enlisted not in self.absent:
            self.absent.append(enlisted)
            return False

        return True

    def get_embeded(self):

        if self.name is not None:
            embed = discord.Embed(title=f':exclamation: __{self.name}!__ :exclamation: ',
                                  colour=discord.Colour.blurple())
        else:
            embed = discord.Embed(title=f':exclamation: __{self.location}!__ :exclamation: ',
                                  colour=discord.Colour.blurple())
        # embed.set_author(name='Test')
        if self.image_url is not None:
            embed.set_image(url=self.image_url)
        # else:

        wartime = parse_date(self.war_time)
        if wartime is None:
            wartime = ''
        if not isinstance(wartime, str):
            ts = int(wartime.timestamp())
            wartime = f'<t:{ts}:f> (<t:{ts}:R>)'
        if self.name is None:
            embed.add_field(name='Details',
                            value=f'📆 {wartime}\n📣 {self.owners}',
                            inline=False)
        else:
            embed.add_field(name='Details',
                            value=f'📆 {wartime}\n📣 {self.owners}\n📍 {self.location}',
                            inline=False)
        if self.attacking is not None:
            # embed.set_thumbnail(url='https://pbs.twimg.com/profile_images/1392124727976546307/vBwCWL8W_400x400.jpg')
            embed.add_field(name='Attackers', value=f'{self.attacking}', inline=True)
            embed.add_field(name='Defenders', value=self.defending, inline=True)
            embed.add_field(name='\u200b', value='\u200b', inline=False)

            # self.groups.embed(embed)

        # if self.looking_for is not None:
        #     embed.add_field(name='Looking for', value=self.looking_for, inline=False)

        if self.additional_info is not None:
            info = self.additional_info
            if len(info) >= 1018:
                info = self.additional_info[:1018]
            embed.add_field(name='Additional Info', value=f'```{info}```', inline=False)

        # embed.add_field(name='\u200b', value='\u200b', inline=False)
        embed.add_field(name='Enlisted',
                        value=f'{str(len(self.roster))}',
                        inline=True)
        embed.add_field(name='Absent',
                        value=f'{str(len(self.absent))}',
                        inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)

        if self.private is not None:
            embed.set_footer(text='🔒 Private')

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
                table.append((True, entry))

        for enlisted in self.absent:
            entry = users[enlisted]
            if entry is not None and (filter is None or filter(entry)):
                table.append((False, entry))

        return table

    def embeds(self):
        # ret = [self.get_embeded(), self.groups.embed()]
        # if self.groups is not None and len(self.groups) > 0:
        #     ret.append(self.groups.embed())
        return self.get_embeded()
