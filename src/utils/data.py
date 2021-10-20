import discord


class MessageReference:

    def __init__(self, msg=None, guild_id=None, channel_id=None, message_id=None):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.message_id = message_id

        if msg is not None:
            self.guild_id = msg.guild.id
            self.channel_id = msg.channel.id
            self.message_id = msg.id

    def __dict__(self):
        return {
            'guild_id': int(self.guild_id),
            'channel_id': self.channel_id,
            'message_id': self.message_id
        }

    def get_message(self, client: discord.Client) -> discord.PartialMessage:
        guild: discord.Guild = client.get_guild(int(self.guild_id))
        channel: discord.TextChannel = guild.get_channel(int(self.channel_id))
        message: discord.PartialMessage = channel.get_partial_message(int(self.message_id))
        return message

    def is_channel(self, channel: discord.TextChannel):
        return self.guild_id == channel.guild.id and self.channel_id == channel.id

    def key(self):
        return f'{self.guild_id}.{self.channel_id}.{self.message_id}'


def parse_message_references(data: list):
    result = []
    if isinstance(data, list):
        for item in data:
            result.append(MessageReference(**item))
    elif isinstance(data, dict):
        for guild_id in data:
            dat: dict = data[guild_id]
            mid = dat['mid']
            cid = dat['cid']
            result.append(MessageReference(guild_id=guild_id, channel_id=cid, message_id=mid))

    return result


def store_message_references(data: list):
    result = []
    for item in data:
        result.append(item.__dict__())

    return result


def get_messages_in_channel(channel: discord.TextChannel, refs):
    result = []
    for ref in refs:
        if ref.is_channel(channel):
            result.append(ref)
    return result


def get_message(client, guild_id, channel_id, message_id) -> discord.PartialMessage:
    guild: discord.Guild = client.get_guild(int(guild_id))
    channel: discord.TextChannel = guild.get_channel(int(channel_id))
    message: discord.PartialMessage = channel.get_partial_message(int(message_id))

    return message


class ChannelReference:

    def __init__(self, ch: discord.TextChannel = None, guild_id=None, channel_id=None):
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.channel = None
        if ch is not None:
            self.guild_id = ch.guild.id
            self.channel_id = ch.id

    def resolve(self, client: discord.Client):
        self.channel = self.get_channel(client)

    def __call__(self, client: discord.Client):
        return self.get_channel(client)

    def __dict__(self):
        return {
            'guild_id': self.guild_id,
            'channel_id': self.channel_id,
        }

    def get_channel(self, client: discord.Client) -> discord.TextChannel:
        guild: discord.Guild = client.get_guild(int(self.guild_id))
        channel: discord.TextChannel = guild.get_channel(int(self.channel_id))

        return channel
