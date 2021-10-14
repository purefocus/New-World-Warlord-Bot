import discord
from utils.botutil import *
from config import r2e


class WarStrategy:
    def __init__(self, war, data=None):
        self.war = war
        self.groups = {}

        self.war_board = None

        if data is not None:
            self.from_dict(data)
        else:
            for i in range(10):
                self.groups[i] = {
                    'name': f'Group {i}',
                    'members': {}
                }

        war.groups = self

    def as_dict(self):
        ret = {
            'groups': self.groups
        }
        if self.war_board is not None:
            ret['board'] = self.war_board.as_dict()

        return ret

    def from_dict(self, data: dict):
        if data is None:
            return self

        self.groups = data['groups']
        if 'board' in data:
            self.war_board = MessageReference().from_dict(data['board'])
        return self

    def rename_group(self, group_id, new_name):
        group_id = str(group_id)
        self.groups[group_id]['name'] = new_name

    def unasign(self, user_id):
        entry = self.war.get_by_id(user_id)
        if entry is not None:
            if entry.group is not None:
                group = self.groups[entry.group]
                members = group['members']
                del members[user_id]
                entry.group = None

    def assign_to(self, user_id, group_id, role):
        group_id = str(group_id)
        user_id = str(user_id)
        try:
            self.unasign(user_id)
        except:
            pass
        entry = self.war.get_by_id(user_id)
        if entry is not None:
            members = self.groups[group_id]['members']
            members[user_id] = {
                'id': user_id,
                'name': entry.username,
                'role': role
            }
            entry.group = group_id

    async def update_boards(self, client):
        if self.war_board is not None:
            await self.war_board.get_message(client).edit(embed=self.create_embed())

    def create_embed(self, embed=None):
        flag = True
        if embed is None:
            flag = False
            embed = discord.Embed(title='War Group',
                                  description=f'Group Assignments for the war on {self.war.location}')

        for i in range(10):
            group = self.groups[str(i)]

            title = group['name']
            members = group['members']
            size = len(members)
            member_list = ''

            for key in members:
                mem = members[key]
                name = mem['name']
                id = mem['id']
                role = mem['role']
                if role in r2e:
                    role = r2e[role]
                else:
                    role = f'({role})'
                member_list += f'{id} :: {name} {role}\n'

            for j in range(size, 5):
                member_list += f'---\n'

            embed.add_field(name=title, value=member_list)

        if not flag:
            embed.set_footer(text='War Managers: Use /assign to assign people to groups')

        return embed
