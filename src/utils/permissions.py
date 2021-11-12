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


master_users = [198526201374048256]

permissions = {
    cfg.LOTUS_SERVER_ID: {
        Perm.ADMIN: ['Moderator', 'Governor', 'Consul'],
        Perm.ENLIST: ['Guest', 'Member', 'Ally', 'Ambassador'],
        Perm.WAR_CREATE: ['Warden Leader'],
        Perm.WAR_END: Perm.WAR_END,
        Perm.WAR_ROSTER: ['Warden Leader'],
        Perm.WAR_POST: Perm.WAR_ROSTER,
        Perm.CONFIGURE: []
    },
    cfg.FACTION_SERVER_ID: {
        Perm.ADMIN: ['Moderators', 'Admin'],
        Perm.ENLIST: ['Verified'],
        Perm.WAR_CREATE: ['Governor', 'Consul'],
        Perm.WAR_END: Perm.WAR_END,
        Perm.WAR_ROSTER: ['Governor', 'Consul', 'Officer'],
        Perm.WAR_POST: Perm.WAR_ROSTER,
        Perm.CONFIGURE: []
    },
    cfg.WARLORD_TEST_ID: {
        Perm.ADMIN: [],
        Perm.ENLIST: [],
        Perm.WAR_CREATE: [],
        Perm.WAR_END: [],
        Perm.WAR_ROSTER: [],
        Perm.WAR_POST: [],
        Perm.CONFIGURE: []
    },
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
    if user.guild.id != cfg.FACTION_SERVER_ID:
        faction_guild = client.get_guild(cfg.FACTION_SERVER_ID)
        try:
            user = await faction_guild.fetch_member(user.id)
            if user is None:
                return False

            return has_permission(user, p)

        except Exception as e:
            print(str(e))
    return False


def has_permission(user: discord.Member, p: Permission) -> bool:
    if user.id in master_users:
        print(f'Master Permission Bypass! {user.display_name} ({user})')
        return True

    guild = user.guild
    if p.faction_only and user.guild.id != cfg.FACTION_SERVER_ID:
        return False

    if guild.id in permissions:
        perms = permissions[guild.id]
        if p in perms:
            allowed = perms[p]
            if isinstance(allowed, Permission):
                allowed = perms[p]

            for role in allowed:
                if has_role(user, role):
                    return p.allow
    return not p.allow


async def check_permission(ctx: discord_ui.Interaction, p: Permission) -> bool:
    if not has_permission(ctx.author, p):
        await respond_deny(ctx)
        return False
    return True


async def respond_deny(ctx: discord_ui.Interaction):
    if not ctx.responded:
        await ctx.respond('You don\'t have permission to do this!', hidden=True)