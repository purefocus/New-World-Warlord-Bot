from discord import Embed
import discord


class User:

    def __init__(self, discord_user: str, username: str, level: int, faction: str, company: str, weapons: str):
        self.discord_user = discord_user
        self.username = username
        self.level = level
        self.faction = faction
        self.company = company
        self.weapons = weapons

    def embed(self):
        pass

    def get_user(self, guild: discord.Guild):
        guild.get_member_named(self.discord_user)

    def send_message(self, message: str, client: discord.Client):
        pass
