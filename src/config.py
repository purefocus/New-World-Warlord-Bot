import json
import discord
from discord_ui import SlashPermission
from utils.colorprint import *
import os

FILES_DIR = '../files'
CFG_FILE = os.path.join(FILES_DIR, 'config.json')
TMP_DIR = os.path.join(FILES_DIR, '.tmp')
WAR_DATA = os.path.join(FILES_DIR, 'wardata.json')

BOT_TOKEN_FILE = os.path.join(FILES_DIR, 'token.json')
if not os.path.exists(FILES_DIR):
    os.mkdir(FILES_DIR)
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)

WAR_ROLES = ['DPS', 'Healer', 'Tank', 'Siege', 'Sharpshooter']

WEAPON_CHOICES = ['Sword and Shield', 'Rapier', 'Hatchet',  # One handed
                  'Spear', 'Great Axe', 'War Hammer',  # 2 handed
                  'Bow', 'Musket',  # Ranged
                  'Fire Staff', 'Life Staff', 'Ice Gauntlet']  # Magic

FACTIONS = ['Syndicate', 'Covenant', 'Marauders']

r2e = {
    'DPS': ':axe:',
    'Healer': ':adhesive_bandage:',
    'Tank': ':shield:',
    'Siege': ':hammer_pick:',
    'Sharpshooter': ':bow_and_arrow:'
}


def tmpfile(file):
    return os.path.join(TMP_DIR, file)


class Config:

    def __init__(self):
        self.bot_token = None
        # self.war_board_channels = [
        #     {'gid': 897098434153185290, 'cid': 897161705333858346},  # Test Server
        #     {'gid': 894675526776676382,
        #      'cid': 896290527622869003,  # #war-boards
        #      # 'cid': 895494342653927435  # bot-setup-and-data
        #
        #      }  # 895494342653927435} # Syndicate Group Server
        # ]
        # self.war_signup_channels = [
        #     {'gid': 897098434153185290, 'cid': 897114437553647636},  # Test Server
        #     {'gid': 894675526776676382,
        #      'cid': 896289677164822578,  # #war-signup
        #      # 'cid': 895494342653927435  # bot-setup-and-data
        #
        #      }  # 895494342653927435} # Syndicate Group Server
        # ]
        self.war_notice_channels = {
            '897098434153185290': '897161705333858346',  # Test server: wars
            '894675526776676382': '896290527622869003'
        }
        self.war_signup_channels = {
            '897098434153185290': '897114437553647636',  # Test server: war-signup
            '894675526776676382': '896289677164822578'
        }
        self.war_management_channels = {
            '897098434153185290': '898221091372298250',  # Test server: war-management
            '894675526776676382': '896290527622869003'
        }
        self.question_timeout = int(60 * 5)

        guild_ids = [897098434153185290, 894675526776676382]
        guild_ids_testing = [897098434153185290]
        guild_permissions = {
            897098434153185290: SlashPermission(allowed={"897191745060745297": SlashPermission.ROLE}),
            894675526776676382: SlashPermission(allowed={"895472067850424370": SlashPermission.ROLE,  # Consul
                                                         '895471923134341200': SlashPermission.ROLE,  # Governor
                                                         '894677353479942154': SlashPermission.ROLE,  # Admin
                                                         '198526201374048256': SlashPermission.USER})  # purefocus
        }

        self.cmd_cfg_elev = {
            'guild_ids': guild_ids,
            'default_permission': False,
            'guild_permissions': guild_permissions
        }
        self.cmd_cfg = {
            'guild_ids': guild_ids
        }

        self.config = {
            'guilds': {
                '897098434153185290': {
                    'name': 'Warlord Test Server',
                    'channels': {
                        'signup': 'war-signup',
                        'listings': 'wars'
                    },
                    'permissions': {
                        'enlist': [
                            {'name': 'WarAdmin',
                             'id': '897191745060745297',
                             'type': 'role'
                             },
                            {'name': '@purefocus#3061',
                             'id': '198526201374048256',
                             'type': 'user'
                             }
                        ],
                        'create': [
                            {'name': 'WarAdmin',
                             'id': '897191745060745297',
                             'type': 'role'
                             },
                            {'name': '@purefocus#3061',
                             'id': '198526201374048256',
                             'type': 'user'
                             }
                        ],
                        'manage': [
                            {'name': 'WarAdmin',
                             'id': '897191745060745297',
                             'type': 'role'
                             },
                            {'name': '@purefocus#3061',
                             'id': '198526201374048256',
                             'type': 'user'
                             }
                        ],
                    }
                }
            }
        }
        self.guilds = {}
        gdict = self.config['guilds']
        for guild_key in gdict:
            self.guilds[guild_key] = GuildConfig(guild_key, gdict[guild_key])

    def resolve(self, client: discord.Client):
        for guild in client.guilds:
            guild: discord.Guild = guild
            if guild.id in self.guilds:
                self.guilds[guild.id].resolve(guild)

        print_dict(self.guilds)

        self.save()

    def get_signup_channels(self, client: discord.Client):
        channels = []
        for guild in client.guilds:
            if str(guild.id) in self.war_signup_channels:
                channels.append(guild.get_channel(int(self.war_signup_channels[str(guild.id)])))
        return channels

    def get_notice_channels(self, client: discord.Client):
        channels = []
        for guild in client.guilds:
            if str(guild.id) in self.war_notice_channels:
                channels.append(guild.get_channel(int(self.war_notice_channels[str(guild.id)])))
        return channels

    def is_war_management(self, msg: discord.Message):
        gid = str(msg.guild.id)
        return gid in self.war_management_channels \
               and str(msg.channel.id) == self.war_management_channels[gid]

    def is_war_signup(self, msg: discord.Message):
        gid = str(msg.guild.id)
        return gid in self.war_signup_channels \
               and str(msg.channel.id) == self.war_signup_channels[gid]

    def save(self):
        try:
            json.dump(self.config, open(CFG_FILE, 'w+'), indent=4)
        except Exception as e:
            print(e)

    def load(self):
        try:
            info = json.load(open(BOT_TOKEN_FILE, 'r'))
            self.bot_token = info['token']
        except:
            json.dump({'token': '<token goes here'}, open(BOT_TOKEN_FILE, 'w+'))
            raise Exception(f'Need bot token! Add the token to {BOT_TOKEN_FILE}!')
        try:
            self.config = json.load(open(CFG_FILE, 'r'))
        except Exception as e:
            print(e)


class GuildConfig:

    def __init__(self, guild_key, cfg=None):
        self.name = cfg['name']
        self.id = guild_key
        self.cfg = cfg
        self.resolved_cfg = {}

        self.guild: discord.Guild = None
        self.signup: discord.TextChannel = None
        self.boards: discord.TextChannel = None

    def resolve(self, guild: discord.Guild):
        self.guild = guild
        channels = self.cfg['channels']

        for channel in guild.text_channels:
            channel: discord.TextChannel = channel
            if channel.name == channels['signup']:
                self.signup = channel

            if channel.name == channels['listings']:
                self.boards = channel

        return self

    def _check_channel(self, cfg, channel: discord.TextChannel):
        if channel.name == cfg['name']:
            cfg['name'] = channel.name

    def ch_signup(self) -> discord.TextChannel:
        return self.signup

    def ch_boards(self) -> discord.TextChannel:
        return self.boards

    def __dict__(self):
        ret = {
            'name': self.guild.name,
            'channels': {
                'signup': self.signup.name if self.signup is not None else None,
                'listings': self.boards.name if self.boards is not None else None
            },
            'permissions': {
                'enlist': [
                    {'name': 'WarAdmin',
                     'id': '897191745060745297',
                     'type': 'role'
                     },
                    {'name': '@purefocus#3061',
                     'id': '198526201374048256',
                     'type': 'user'
                     }
                ],
                'create': [
                    {'name': 'WarAdmin',
                     'id': '897191745060745297',
                     'type': 'role'
                     },
                    {'name': '@purefocus#3061',
                     'id': '198526201374048256',
                     'type': 'user'
                     }
                ],
                'manage': [
                    {'name': 'WarAdmin',
                     'id': '897191745060745297',
                     'type': 'role'
                     },
                    {'name': '@purefocus#3061',
                     'id': '198526201374048256',
                     'type': 'user'
                     }
                ],
            }
        }
        return ret
