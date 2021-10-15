import discord
from dat.UserSignup import *
from dat.EnlistDef import *
from dat.WarStrategy import WarStrategy


class WarDef:

    def __init__(self, data=None):
        self.id = None
        self.active = False

        self.attacking = None
        self.defending = None

        self.location = None
        self.war_time = None
        self.owners = None
        self.enlisted = Enlisted()
        self.war_board = {}

        self.groups = WarStrategy(self)

        if data is not None:
            self.from_dict(data)

    def as_dict(self):
        ret = {
            'active': self.active,
            'attacking': self.attacking,
            'defending': self.defending,
            'location': self.location,
            'wartime': self.war_time,
            'owners': self.owners,
            'enlisted': self.enlisted.as_dict(),
            'boards': self.war_board,
            'groups': self.groups.as_dict()
        }
        return ret

    def from_dict(self, dic):
        self.active = dic['active']
        self.attacking = dic['attacking']
        self.defending = dic['defending']
        self.location = dic['location']
        self.war_time = dic['wartime']
        self.owners = dic['owners']
        self.war_board = dic['boards']
        self.enlisted = Enlisted(dic['enlisted'])

        self.groups.from_dict(dic['groups'])

        return self

    def add_board(self, msg: discord.Message):
        self.war_board[msg.guild.id] = {'cid': msg.channel.id, 'mid': msg.id}

    def add_enlistment(self, enlisted) -> bool:
        name = self.enlisted.is_enlisted(enlisted)
        if name is not None:
            enlisted.id = self.enlisted[name].id
        self.enlisted.enlist(enlisted)
        return name is not None

    def get_embeded(self):
        embed = discord.Embed(title='War! [Beta]')
        embed.add_field(name='Details',
                        value=f'Location: {self.location}\nTime: {self.war_time}\nContact: {self.owners}',
                        inline=False)

        embed.add_field(name='Attackers', value=self.attacking, inline=True)
        embed.add_field(name='Defenders', value=self.defending, inline=True)

        embed.add_field(name='Enlisted', value=str(len(self.enlisted)), inline=False)

        embed.set_footer(text='Use /enlist to signup for this war!')

        return embed

    def get_by_id(self, id):
        for enlisted in self.enlisted:
            entry = self.enlisted[enlisted]
            if entry.id == id:
                return entry
        return None

    def __repr__(self):
        return f'{self.location}'

    def create_table(self, filter=None):

        table = [['Name', 'Level', 'Faction', 'Company', 'Role', 'Weapons']]
        for enlisted in self.enlisted:
            entry = self.enlisted[enlisted]
            if filter is None or filter(entry):
                table.append(entry.make_table_row())

        return table
