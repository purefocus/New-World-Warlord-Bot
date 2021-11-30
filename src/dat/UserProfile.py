import discord

from utils.discord_utils import get_company_role


class UserProfile:

    def __init__(self, user: discord.Member, cfg, users=None):  # name_enforcement=False, company_enforcement=False):
        self.company = get_company_role(user) if cfg.company_enforcement else None

        self.username = user.display_name if cfg.name_enforcement else None
        self.discord_user = str(user)
        self.user_data = None if users is None else users[self.username]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.username is None:
            return f'{self.discord_user}'

        if self.company is not None:
            return f'{self.username} ({self.company})'
        else:
            return f'{self.username}'

    def embed(self):
        embed = discord.Embed()
        embed.add_field(name='Username', value=self.username)
        embed.add_field(name='Company', value=self.company)
        return embed
