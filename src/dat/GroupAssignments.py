import dat.EnlistDef
import discord
from utils.details import replace_emojis


class GroupAssignments:

    def __init__(self, data: dict = None, war=None):
        self.war = war
        if data is not None:
            self.data = data
        else:
            self.data = {
                'groups': {
                }
            }

    def update_group(self, group_id: str, name: str = None, members: list = None):
        if group_id not in self.data['groups']:
            group = self.data['groups'][group_id] = {
                'name': None,
                'members': {}
            }
        else:
            group = self.data['groups'][group_id]

        if name is not None:
            group['name'] = name

        if members is not None:
            group['members'] = {}
            for member, role in members:
                memdict = group['members']
                memdict[member] = role

    def from_dict(self, data: dict):
        self.data = data

    def __dict__(self):
        return self.data

    def __len__(self):
        return len(self.data['groups'])

    def embed(self, embed=None) -> discord.Embed:
        if embed is None:
            embed = discord.Embed(title='Group Assignments')
        else:
            embed.add_field(name='\n Group Assignments\n', value='-', inline=False)

        groups = self.data['groups']
        for group in groups:
            group: dict = groups[group]
            name = group['name']
            members = group['members']
            if name is None:
                name = group

            value = ''
            for member in members:
                role = members[member]
                value += f'\n - {member} '
                if role is not None:
                    value += replace_emojis(role.replace(',', ''))

            if len(members) == 0:
            # for i in range(len(members), 5):
                value += '\n - '

            embed.add_field(name=f'__{name}__', value=value)

        return embed
