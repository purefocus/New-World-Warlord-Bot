import discord
from discord.ext import commands
from discord_ui.cogs import slash_cog, subslash_cog, listening_component_cog
from bot_state import BotState

import discord_ui
from discord_ui import SlashOption, SlashPermission, SlashedCommand
from discord_ui import Interaction
from views.weapon_selection import ask_weapon_mastery
from views.view_confirm import ask_confirm

from utils.botutil import print_stack_trace
from utils.discord_utils import *
import pandas as pd
import os
from utils.colorprint import *

import config as cfg

admin_cmd_cfg = {
    'guild_ids': [894675526776676382],
    'guild_permissions': {
        894675526776676382: SlashPermission(
            allowed={
                '894677353479942154': SlashPermission.Role,  # Admin
                '895490018246815776': SlashPermission.Role,  # Moderator
                '198526201374048256': SlashPermission.User  # purefocus
            }
        )
    }
}


def _get_all_faction_roles(guild: discord.Guild):
    factions = []
    non_factions = []
    for role in guild.roles:
        if role.colour.value == 0xb9adff:
            factions.append(role.name)
        else:
            non_factions.append(role.name)

    print('Factions: ', factions)
    print('Non Factions: ', non_factions)


async def _make_company_role(name: str, guild: discord.Guild):
    role = await guild.create_role(name=name,
                                   colour=discord.Colour(0xb9adff),
                                   permissions=discord.Permissions(permissions=2147863617),
                                   hoist=True,
                                   mentionable=False,
                                   reason='Adding a new company tag')
    return role


class AdminCog(commands.Cog):

    def __init__(self, client: commands.Bot, state: BotState, ui: discord_ui.UI):
        self.client = client
        self.state = state
        self.ui = ui

    @slash_cog(name='test_cmd', options=[
        SlashOption(str, 'arguments', 'command args', required=True)
    ], **admin_cmd_cfg)
    async def test_cmd(self, ctx: discord_ui.SlashedCommand, arguments: str):
        args = arguments.split(' ')
        try:
            if len(args) == 0:
                await ctx.respond('test!', hidden=True)
            elif args[0] == 'new' and args[1] == 'faction':
                await ctx.respond('Changed to `/admin company create <company name>`', hidden=True)

            elif args[0] == 'guide':
                from views.Guide import create_embed
                embed = create_embed()
                await ctx.send(embed=embed)

            elif args[0] == 'tag':
                self.state.config.tag_war = args[1] == 'en'

            elif args[0] == 'test':
                embed = discord.Embed(title='Testing Something...')
                embed.add_field(name='Test', value='> test1\n> test2')
                await ctx.respond(embed=embed, hidden=True)

            elif args[0] == 'dup_check':
                guild: discord.Guild = ctx.guild
                name = args[1]
                matches = check_for_matching_name(name, guild)
                result = 'Checking for duplicated names...\n\n'
                if len(matches) == 0:
                    result = 'No matching names found!'
                else:
                    for m in matches:
                        result += f'  - {m.mention} (*{m.joined_at.strftime("%m/%d/%y")}*)\n'

                await ctx.respond(content=result)

            elif args[0] == 'dup_names':
                guild: discord.Guild = ctx.guild
                result = 'Checking for duplicated names...\n'
                matches = search_for_duplicate_names(guild)
                for key, matched in matches:
                    result += f'  Matched Name: **{key}**\n'
                    for m in matched:
                        result += f'    - {m.mention} (*{m.joined_at.strftime("%m/%d/%y")}*)\n'

                # names = {}
                # for mem in guild.members:
                #     name = mem.display_name.lower()
                #     if name in names:
                #         other = names[name]
                #         result += f'- {name}: {mem.mention} ({mem.joined_at.strftime("%m/%d/%y")}), {other.mention} ({other.joined_at.strftime("%m/%d/%y")})\n'
                #     names[name] = mem

                await ctx.respond(content=result)

            elif args[0] == 'verified':
                hidden = True
                if len(args) == 2:
                    hidden = not args[1] == 'show'
                await ctx.defer(hidden=hidden)
                data = await get_verified_users(ctx.guild)

                data = pd.DataFrame(data, columns=['Name', 'Company', 'Rank'])

                file = os.path.join(cfg.TMP_DIR, 'verified.xlsx')

                data.to_excel(file, index=True, header=True)

                await ctx.respond(f'Here is a full list of *verified* users!\nFound {len(data)} verified users!',
                                  file=discord.File(file), hidden=hidden)
            elif args[0] == 'companies':
                hidden = True
                if len(args) == 2:
                    hidden = not args[1] == 'show'
                await ctx.defer(hidden=hidden)
                data = await get_companies(ctx.guild)

                table = []
                for name in data:
                    try:
                        company = data[name]
                        members = len(company['members'])
                        governor = company['Governor']
                        officers = len(company['Officer'])
                        consuls = len(company['Consul'])
                        settlers = len(company['Settler'])
                        lg = len(governor)
                        if lg == 0:
                            governor = None
                        else:
                            governor = ', '.join(governor)
                        table.append([name, governor, members, consuls, officers, settlers])
                    except:
                        print_dict(company)
                        return

                table = sorted(table, key=lambda x: x[0])

                headers = ['Company', 'Governor(s)', '# Members', '# Consuls', '# Officers', '# Settlers']
                data = pd.DataFrame(table, columns=headers)

                file = os.path.join(cfg.TMP_DIR, 'companies.xlsx')

                data.to_excel(file, index=True, header=True)

                await ctx.respond(f'Here is a full list of registered companies!\nFound {len(data) - 1} companies!',
                                  file=discord.File(file), hidden=hidden)

                # await ctx.respond(ninja_mode=True)
            elif args[0] == 'verify_btn':
                await ctx.channel.send(content='Click this button to verify!', components=[
                    discord_ui.Button(custom_id='btn:verification_btn', label='Click here to verify!', color='green')
                ])
                await ctx.respond('Done.', hidden=True)




        except Exception as e:
            await ctx.send(str(e), hidden=True)
            bu.print_stack_trace()

        # guild.create_role(name=faction)

    @slash_cog(name='warlord_cmd_sync')
    async def warlord_cmd_sync(self, ctx: SlashedCommand):
        try:
            if ctx.author.id == 198526201374048256:
                msg = await ctx.send(content='Removing all Commands... ', hidden=True)
                await self.ui.slash.nuke_commands()
                await msg.edit(content=f'{msg.content}\nAdding Commands...')
                print('Commands Before: ', self.state.client.commands)
                await self.ui.slash.sync_commands()
                print('Commands After: ', self.state.client.commands)
                await msg.edit(content=f'{msg.content}\nCommand Sync Complete!')
        except Exception as e:
            print_stack_trace()
            await ctx.respond(content=str(e), hidden=True)
        print('Done')

    @slash_cog(name='warlord_reboot')
    async def warlord_reboot(self, ctx: SlashedCommand):
        try:
            if ctx.author.id == 198526201374048256:
                confirm = await ask_confirm(self.state, ctx, f'Are you sure you want to reboot Warlord?')
                if confirm:
                    await ctx.respond(content='Rebooting...', hidden=True)
                    import sys
                    sys.exit(1)
                else:
                    await ctx.respond(content='Reboot Canceled!', hidden=True)
        except Exception as e:
            print_stack_trace()
            await ctx.respond(content=str(e), hidden=True)

    # @slash_cog(name='admin', guild_ids=[894675526776676382], guild_permissions=guild_permissions)
    # async def cmd_admin(self, ctx: SlashedCommand):
    #     await ctx.send('base command!')

    @subslash_cog(base_names=['admin', 'company'], name='create', options=[
        SlashOption(str, name='Name', description='Name of the company you wish to create', required=True)
    ], **admin_cmd_cfg)
    async def cmd_admin_company(self, ctx: SlashedCommand, name: str):
        guild: discord.Guild = ctx.guild

        # _get_all_faction_roles(guild)
        found = False
        for role in guild.roles:
            role: discord.Role = role
            if role.name.lower() == name.lower():
                found = True

        if found:
            await ctx.respond('The role already exists!', hidden=True)
        else:
            add_role, msg = await ask_confirm(self.state, ctx,
                                              f'Would you like to add the new faction role **{name}**?', ret_msg=True)
            if add_role:
                await _make_company_role(name, guild)

            await msg.edit(
                f'Role {name} Added!\n *Don\'t forget to change the role\'s position in the server role list!*',
                components=None)
