import discord

from utils.discord_utils import get_company_role


class UserProfile:

    def __init__(self, user: discord.Member):
        self.company = get_company_role(user)
        self.username = user.display_name
        self.discord_user = str(user.mention)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        if self.company is not None:
            return f'{self.username} ("{self.company}") [{self.discord_user}]'
        else:
            return f'{self.username} [{self.discord_user}]'
