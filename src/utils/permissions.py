import discord
import discord_ui
from utils.discord_utils import has_role

import config as cfg

from utils.colorprint import print_dict


class Permission:

    def __init__(self, key, whitelist, faction_only_permission=False):
        self.key = key
        self.allow = whitelist
        self.faction_only = faction_only_permission

    def __repr__(self):
        return self.key


class Perm:
    ENLIST = Permission('enlist', True)
    WAR_CREATE = Permission('war_create', True)
    WAR_MANAGEMENT = Permission('war_manage', True)
    WAR_END = Permission('war_end', True)
    WAR_ROSTER = Permission('war_roster', True)
    WAR_POST = Permission('war_post', True)
    CONFIGURE = Permission('configure', True)
    ADMIN = Permission('admin', True)
    WAR_HOST = Permission('war_host', True)


master_users = [198526201374048256]
# /message_enlisted message: Sorry for the spam, but this is just a test
permissions = {
    # cfg.FACTION_SERVER_ID: {
    #     Perm.ADMIN: ['Moderators', 'Admin'],
    #     Perm.ENLIST: ['Verified'],
    #     Perm.WAR_CREATE: ['Governor', 'Consul'],
    #     Perm.WAR_END: Perm.WAR_CREATE,
    #     Perm.WAR_ROSTER: ['Governor', 'Consul', 'Officer'],
    #     Perm.WAR_POST: Perm.WAR_ROSTER,
    #     Perm.CONFIGURE: [],
    #     Perm.WAR_HOST: ['War Manager']
    # },
    cfg.FACTION_SERVER2_ID: {
        Perm.ADMIN: ['Mods', 'Admin'],  # Global permissions to everything
        Perm.ENLIST: ['Syndicate Verified'],  # Permission to enlist in a war
        Perm.WAR_CREATE: ['Governor', 'Consul'],  # Create a new war post
        Perm.WAR_END: Perm.WAR_CREATE,  # Can end a war
        Perm.WAR_ROSTER: ['Governor', 'Consul', 'Officer'],  # Can pull/download the roster for a war
        Perm.WAR_POST: Perm.WAR_ROSTER,  # Can re-post war notifications and enlistment links
        Perm.CONFIGURE: [],  # Can change bot configuration
        Perm.WAR_HOST: ['War Manager']  # (Work in Progress)
    },
    cfg.WARLORD_TEST_ID: {
        Perm.ADMIN: ['WarAdmin'],
        Perm.ENLIST: [],
        Perm.WAR_CREATE: [],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: [],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    },
    cfg.ACTUAL_APES_ID: {
        Perm.ADMIN: ['Server Admin', 'Consul', 'Gorillas'],
        Perm.ENLIST: ['Apes', 'War Fighter', 'Scrimps', '*'],
        Perm.WAR_CREATE: [],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: [],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Stormys Cloud
    850011885574815754: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Stormuwu', 'Consul'],
        Perm.ENLIST: ['Storm Chasers', 'Cuties'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Storm Chasers Discord
    897255450054127637: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Stormuwu', 'Consul'],
        Perm.ENLIST: ['Storm Chasers', 'Cuties', 'Syndicate', 'Covenant', 'Marauders', 'Allies', '*'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Goblin Loot Corpse
    895073382465425418: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Stormuwu', 'Governor', 'Consul'],
        Perm.ENLIST: ['Goblin'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Silver Dawn
    892519781759070218: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Stormuwu', 'Governor', 'Consul'],
        Perm.ENLIST: ['Settler'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Scrimps
    905475600364498974: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Governor', 'Consul', 'Scrimp Lord', 'Scrimp King'],
        Perm.ENLIST: ['Scrimp'],
        Perm.WAR_CREATE: ['Scrimp Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Shadow Pack
    894043484191867011: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Governor', 'Consul'],
        Perm.ENLIST: ['Shadow Pack', 'Syndicate'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Gremlin
    919685476850491442: {
        Perm.ADMIN: ['Moderator', 'Admin', 'Governor', 'Consul'],
        Perm.ENLIST: ['Friend of the Gremlins', 'Syndicate'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Amazonian Primez
    785469845487353877: {
        Perm.ADMIN: ['All Might', 'Marked Ones', 'Chancellor'],
        Perm.ENLIST: ['Amazonian Primez'],
        Perm.WAR_CREATE: ['Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }, # Unhinged
    614191241525067776: {
        Perm.ADMIN: ['Leadership', 'Server Admin'],
        Perm.ENLIST: ['Member', 'Company Member', 'new world'],
        Perm.WAR_CREATE: ['Company Officer'],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: ['Officer'],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: [],
        Perm.WAR_HOST: []
    }
}

for guild in permissions:
    guild_perms = permissions[guild]
    admins = guild_perms[Perm.ADMIN]
    for key in guild_perms:
        if key != Perm.ADMIN:
            perms = permissions[guild][key]
            if isinstance(perms, Permission):
                continue
            for admin in admins:
                perms.append(admin)


async def check_faction_permission(user: discord.Member, p: Permission, client: discord.Client) -> bool:
    if user.guild.id != cfg.FACTION_SERVER2_ID:
        faction_guild = client.get_guild(cfg.FACTION_SERVER2_ID)
        try:
            user = await faction_guild.fetch_member(user.id)
            if user is None:
                return False

            return has_permission(user, p)

        except Exception as e:
            print(str(e))
    return False


def has_permission(user: discord.User, p: Permission) -> bool:
    if user.id in master_users:
        # print(f'Master Permission Bypass! {user.display_name} ({user})')
        return True
    # print(type(user))
    # guild = user.guild
    for guild in user.mutual_guilds:
        user = guild.get_member(user.id)
        if p.faction_only and guild.id != cfg.FACTION_SERVER2_ID:
            return False

        if guild.id in permissions:
            perms = permissions[guild.id]
            if p in perms:
                allowed = perms[p]
                if isinstance(allowed, Permission):
                    allowed = perms[allowed]

                for role in allowed:

                    if has_role(user, role) or role == '*':
                        # print(f'allowed by role {role}')
                        return p.allow
    return not p.allow


async def check_permission(ctx: discord_ui.Interaction, p: Permission) -> bool:
    if not has_permission(ctx.author, p):
        print(str(ctx.author), ' does not have the ', p.key, ' permission!')
        await respond_deny(ctx)
        return False
    return True


async def respond_deny(ctx: discord_ui.Interaction):
    if not ctx.responded:
        await ctx.respond('You don\'t have permission to do this!', hidden=True)
