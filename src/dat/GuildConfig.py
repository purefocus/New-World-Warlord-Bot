import discord
import json

configs = {}


def load_guild_configs(client: discord.Client):
    # try:
    #     jconf = json.load(open('guildcfg.json', 'rb'))
    # except Exception e:
    #     jconf = None
    # for g in client.guilds:
    #     guild: discord.Guild = g
    #     cf = jconf[guild.id]
    #
    #     cfg = GuildConfig()
    #     cfg.guild_id = guild.id
    #     cfg.guild_name = guild.name
    #     cfg.war_board_channel = cf['war_board_channel']
    #     cfg.war_create_role = cf['war_create_role']
    #
    #     configs[cfg.guild_id] = cfg
    pass


class MessageInstance:

    def __init__(self, msg: discord.Message):
        self.guild_id = msg.guild.id
        self.channel_id = msg.channel.id
        self.message_id = msg.id

    def get(self, client: discord.Client) -> discord.Message:
        guild: discord.Guild = client.get_guild(self.guild_id)
        channel: discord.TextChannel = guild.get_channel(self.channel_id)
        return channel.get_partial_message(self.message_id)


class GuildConfig:

    def __init__(self):
        self.guild_id = None
        self.guild_name = None
        self.war_board_channel = None
        self.war_create_role = None
