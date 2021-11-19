import json
import discord
from discord_ui import SlashPermission
from utils.colorprint import *
from utils.data import *
import os

FILES_DIR = '../../files'
CFG_FILE = os.path.join(FILES_DIR, 'bot_config.json')
TMP_DIR = os.path.join(FILES_DIR, 'tmp')
WAR_DATA = os.path.join(FILES_DIR, 'wars.json')
USER_DATA = os.path.join(FILES_DIR, 'user_data.json')

BOT_TOKEN_FILE = os.path.join(FILES_DIR, 'token.json')
if not os.path.exists(FILES_DIR):
    os.mkdir(FILES_DIR)
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


def tmpfile(file):
    return os.path.join(TMP_DIR, file)


WARLORD_TEST_ID = 897098434153185290
FACTION_SERVER_ID = 894675526776676382
LOTUS_SERVER_ID = 868924409115709480

guild_ids = [WARLORD_TEST_ID, LOTUS_SERVER_ID, FACTION_SERVER_ID]
fguild_ids = [WARLORD_TEST_ID, FACTION_SERVER_ID]
# guild_ids_testing = [WARLORD_TEST_ID]
guild_permissions_low = {
    WARLORD_TEST_ID: SlashPermission(allowed={'897191745060745297': SlashPermission.ROLE,  # WarAdmin
                                              '198526201374048256': SlashPermission.USER}),  # purefocus
    FACTION_SERVER_ID: SlashPermission(allowed={'895466455766802442': SlashPermission.ROLE,  # Verified
                                                '198526201374048256': SlashPermission.USER}),  # purefocus
    LOTUS_SERVER_ID: SlashPermission(allowed={'895466455766802442': SlashPermission.ROLE,
                                              '198526201374048256': SlashPermission.USER}),  # Verified
}
guild_permissions = {
    WARLORD_TEST_ID: SlashPermission(allowed={"897191745060745297": SlashPermission.ROLE}),
    FACTION_SERVER_ID: SlashPermission(allowed={"895472067850424370": SlashPermission.ROLE,  # Consul
                                                '895471923134341200': SlashPermission.ROLE,  # Governor
                                                '894677353479942154': SlashPermission.ROLE,  # Admin
                                                '895490018246815776': SlashPermission.ROLE,  # Moderator
                                                '198526201374048256': SlashPermission.USER}),  # purefocus
    LOTUS_SERVER_ID: SlashPermission(allowed={'868926287035662418': SlashPermission.ROLE,  # Consul
                                              '868926828235079743': SlashPermission.ROLE,  # Moderator
                                              '868925716736114749': SlashPermission.ROLE,
                                              '198526201374048256': SlashPermission.USER})  # purefocus
}
mod_guild_permissions = {
    WARLORD_TEST_ID: SlashPermission(allowed={"897191745060745297": SlashPermission.ROLE}),
    FACTION_SERVER_ID: SlashPermission(allowed={'894677353479942154': SlashPermission.ROLE,  # Admin
                                                '895490018246815776': SlashPermission.ROLE,  # Moderator
                                                '198526201374048256': SlashPermission.USER}),  # purefocus
    LOTUS_SERVER_ID: SlashPermission(allowed={'868926287035662418': SlashPermission.ROLE,  # Consul
                                              '868926828235079743': SlashPermission.ROLE,  # Moderator
                                              '868925716736114749': SlashPermission.ROLE,
                                              '198526201374048256': SlashPermission.USER})  # purefocus
}
fguild_permissions_low = {
    WARLORD_TEST_ID: SlashPermission(allowed={'897191745060745297': SlashPermission.Role,  # WarAdmin
                                              '198526201374048256': SlashPermission.User}),  # purefocus
    FACTION_SERVER_ID: SlashPermission(allowed={'895466455766802442': SlashPermission.Role,
                                                '198526201374048256': SlashPermission.User}),  # Verified
    LOTUS_SERVER_ID: SlashPermission(allowed={'895466455766802442': SlashPermission.Role,
                                              '198526201374048256': SlashPermission.User}),  # Verified
}

cmd_cfg_elev = {
    # 'guild_ids': guild_ids,
    # 'default_permission': True,
    # 'guild_permissions': guild_permissions
}

cmd_cfg_mod = {
    # 'guild_ids': guild_ids,
    # 'default_permission': True,
    # 'guild_permissions': mod_guild_permissions
}

cmd_cfg = {
    # 'guild_ids': guild_ids,
    # 'default_permission': True,
    # 'guild_permissions': guild_permissions_low
}


# cmd_fcfg = {
#     'guild_ids': fguild_ids,
#     'default_permission': True,
#     'guild_permissions': fguild_permissions_low
# }

# def has_permissions(user: discord.Member, level):


class GuildConfig:

    def __init__(self, guild_key, cfg=None, guild=None):
        self.id = guild_key

        if cfg is not None:
            self.name = cfg['name']
            self.cfg = cfg
        if guild is not None:
            self.name = guild.name
            self.id = guild_key
            self.cfg = {
                'name': self.name,
                'name_enforcement': False,
                'company_enforcement': False,
                'channels': {
                    'signup': None,
                    'notice': None,
                    'management': None
                },
                'permissions': {
                    'verified_roles': [895466455766802442],
                    'privileged_roles': [895471923134341200, 895472067850424370],
                    'admin_roles': [894677353479942154, 895490018246815776]
                }
            }
        self.channels: dict = {
            'signup': None,
            'notice': None,
            'management': None
        }
        self.name_enforcement = self.cfg['name_enforcement']
        self.company_enforcement = self.cfg['company_enforcement']

    def resolve(self, guild: discord.Guild):
        self.guild = guild
        channels = self.cfg['channels']
        self.cfg['name'] = guild.name

        for channel in guild.text_channels:
            channel: discord.TextChannel = channel
            if channel.name == channels['signup']:
                self.channels['signup'] = channel

            if channel.name == channels['notice']:
                self.channels['notice'] = channel

            if channel.name == channels['management']:
                self.channels['management'] = channel

        return self

    def _check_channel(self, cfg, channel: discord.TextChannel):
        if channel.name == cfg['name']:
            cfg['name'] = channel.name

    def set_channel(self, key: str, channel: discord.TextChannel) -> bool:
        chcfg = self.cfg['channels']
        if key in chcfg:
            chcfg[key] = channel.name
            self.channels[key] = channel
            return True

        return False

    def __dict__(self):
        return self.cfg

    async def test_resoved_channels(self):
        for key in self.channels:
            ch = self.channels[key]
            if ch is not None:
                await ch.send(content=f'Test! {key}')


class Config:

    def __init__(self):
        self.bot_token = None
        self.nws_token = None
        self.tag_war = True
        self.unsaved = False
        self.faction_guild = None
        self.question_timeout = int(60 * 5)

        self.config = {
            'guilds': {
                '897098434153185290': {
                    'name': 'Warlord Test Server',
                    'channels': {
                        'signup': 'war-signup',
                        'notice': 'war-notice',
                        'management': 'war-management',
                        'status': 'world-status'
                    }
                }
            }
        }

        self.load()
        self.guilds = {}
        gdict = self.config['guilds']
        for guild_key in gdict:
            self.guilds[guild_key] = GuildConfig(guild_key, gdict[guild_key])

        cfg = self._get(self.config, 'config', {})
        self.announce_signup = self._get(cfg, 'announce_signup', True)
        self.announce_war = self._get(cfg, 'announce_war', True)
        self.tag_war = self._get(cfg, 'tag_war', False)
        self.status = self._get(cfg, 'status', 'online')
        self.game_status = self._get(cfg, 'status_text', 'New World')
        self.verify_channel = self._get(cfg, 'verification_channel', 'verify-your-faction')
        self.mod_verify_channel = self._get(cfg, 'mod_verification_channel', 'verify-requests')

        self.msgs = self._get(self.config, 'messages', {})
        self.status_channels = self._get(self.config, 'status_channels', {})

        for key in self.msgs:
            msgs = self.msgs[key]
            lst = []
            for msg in msgs:
                lst.append(MessageReference(**msg))
            self.msgs[key] = lst

        if self.unsaved:
            self.save()

    def get_messages(self, key):
        if key in self.msgs:
            return self.msgs[key]
        return None

    def register_message(self, key, msg: discord.Message):
        if key not in self.msgs:
            self.msgs[key] = []
        ref = MessageReference(msg=msg)
        self.msgs[key].append(ref)
        self.save()

    def _get(self, cfg: dict, key: str, default):
        if cfg is None:
            cfg = self.config

        if key in cfg:
            return cfg[key]
        cfg[key] = default
        self.unsaved = True
        return default

    def add_guild(self, guild: discord.Guild):
        gc = self.guilds[guild.id] = GuildConfig(str(guild.id), guild=guild)
        self.config['guilds'][guild.id] = gc.__dict__()
        self.save()

    def resolve(self, client: discord.Client):
        try:
            for guild in self.guilds:
                g = client.get_guild(int(guild))
                if g.id == FACTION_SERVER_ID:
                    self.faction_guild = g
                self.guilds[guild].resolve(g)

            self.save()
        except Exception as e:
            print(e)

    async def test_resolved(self):
        for guild in self.guilds:
            guild = self.guilds[guild]
            await guild.test_resoved_channels()

    def _get_channels(self, key):
        result = []
        for g in self.guilds:
            g: GuildConfig = self.guilds[g]
            if key in g.channels:
                channel = g.channels[key]
                if channel is not None:
                    result.append(channel)
        return result

    def get_signup_channels(self):
        return self._get_channels('signup')

    def get_notice_channels(self):
        return self._get_channels('notice')

    def get_management_channels(self):
        return self._get_channels('management')

    def is_channel(self, msg: discord.Message, key):
        channels = self._get_channels(key)
        return msg.channel in channels

    def is_war_management(self, msg: discord.Message):
        return self.is_channel(msg, 'management')

    def is_war_signup(self, msg: discord.Message):
        return self.is_channel(msg, 'signup')

    def is_war_notice(self, msg: discord.Message):
        return self.is_channel(msg, 'notice')

    def guildcfg(self, guild_id) -> GuildConfig:
        guild_id = str(guild_id)
        if guild_id in self.guilds:
            return self.guilds[guild_id]
        return None

    def save(self):
        try:
            for g in self.guilds:
                self.config['guilds'][g] = self.guilds[g].__dict__()

            for key in self.msgs:
                msgs = self.msgs[key]
                lst = []
                for msg in msgs:
                    lst.append(msg.__dict__())
                self.config['messages'][key] = lst

            json.dump(self.config, open(CFG_FILE, 'w+'), indent=2)
            self.unsaved = False
        except Exception as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    def load(self):
        try:
            info = json.load(open(BOT_TOKEN_FILE, 'r'))
            self.bot_token = info['token']
            self.nws_token = info['nws_token']
        except:
            json.dump({'token': '<token goes here>'}, open(BOT_TOKEN_FILE, 'w+'))
            raise Exception(f'Need bot token! Add the token to {BOT_TOKEN_FILE}!')
        try:
            self.config = json.load(open(CFG_FILE, 'r'))

        except Exception as e:
            print(e)
