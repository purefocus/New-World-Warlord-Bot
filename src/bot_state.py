from dat.WarDef import *
import config
import json
import discord
from discord.ext import commands
from discord_ui import Button
from utils.userdata import UserData
from utils.world_status import get_status
import time

from database.tables.users_table import UserRow
from views.roster import create_roster_embed
from views.embeds import user_embed


def _chsum(cond):
    return 1 if cond else 0


def _compare_wars(war, old_war):
    try:
        return _chsum(war.owners == old_war.owners) \
               + (war.war_time == old_war.war_time) \
               + (war.attacking == old_war.attacking) \
               + (war.defending == old_war.defending) \
               + (war.location == old_war.location) \
               + (war.name == old_war.name)
    except:
        return 0


class BotState:

    def __init__(self, client, config):
        self.client: commands.Bot = client
        self.wars = {}
        self.config = config
        self.users: [UserData, None] = UserData()
        self.cogs = {}
        self.ui_client = None

        self.war_selection = {}

        self.world_status = None
        self.db = None

    async def update_presence(self, status):
        start_time = int(1000 * time.time())
        end_time = int(1000 * (time.time() + 60 * 5))
        await self.client.change_presence(
            status=self.config.status,
            activity=discord.Game(
                name=status
            )
        )

    async def add_enlistment(self, disc_name, war: WarDef, user: UserRow, absent=False, save=True, announce=True):
        if user is None:
            print('user is none!?')
            return
        try:
            num_enlisted = len(war)
            # if isinstance(user, UserSignup):
            #     user = user.to_enlistment()
            if absent:
                war.add_absent(user)
            else:
                war.add_enlistment(user)

            self.users.add_user(disc_name, user)

            if self.config.announce_signup and announce:
                await self.announce_signup(user)

            # if num_enlisted != len(war):
            await self.update_war_boards(war)

            if save:
                self.users.save()
                self.save_war_data()

        except Exception as e:

            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    async def announce_signup(self, user):
        if self.config.announce_signup:
            for ch in self.config.get_signup_channels():
                await ch.send(embed=user_embed(user, self))

    def add_war(self, war: WarDef, edit=False):
        if war.is_fake:
            return False
        exists = False
        best_match = None
        if edit:
            best_match = None
            best_score = 0
            for w in self.wars:
                w = self.wars[w]
                if not w.active:
                    continue
                # score = _compare_wars(war, w)
                if w.owners == war.owners and w.active:
                    best_match = w
                # if score > best_score:
                #     best_match = w
                #     best_score = score

        else:
            if war in self.wars:
                # for _w in self.wars:
                w: WarDef = self.wars[war]
                if w.owners == war.owners and w.active:
                    best_match = w
                # best_match = self.wars[war.location]
                # if not best_match.active:
                #     best_match = None
            else:
                best_match = None

        if best_match is not None:
            exists = True
            war.roster = best_match.roster
            war.absent = best_match.absent
            war.boards = best_match.boards
            # war.groups = best_match.groups
            war.id = best_match.id

            # if war.location.lower() != best_match.location.lower():
            #     del self.wars[best_match.id]

        self.wars[war.id] = war
        return exists

    def save_war_data(self):
        saved_data = {}
        for w in self.wars:
            saved_data[w] = self.wars[w].as_dict()

        json.dump(saved_data, open(config.WAR_DATA, 'w+'), indent=4)

        # print('Saved: ', saved_data)

    def load_war_data(self):
        try:
            war_data = json.load(open(config.WAR_DATA, 'r+'))

            for w in war_data:
                self.add_war(WarDef(war_data[w]))

            self.users.load()

            # for w in self.wars:
            #     war: WarDef = self.wars[w]
            #     for user in war.enlisted.roster:
            #         war.add_enlistment(war.enlisted.roster[user])

        except Exception as e:
            self.wars = {}
            raise e

    def get_modifying_war(self, userid):
        if userid in self.war_selection:
            return self.war_selection[userid]
        else:
            return None

    def set_modifying_war(self, userid, war):
        self.war_selection[userid] = war

    async def update_war_boards(self, war: WarDef):
        try:
            need_save = False
            for board in war.boards:
                try:
                    msg: discord.Message = await board.get_message(client=self.client)
                    if msg is not None:
                        await msg.edit(**self.create_board(war))
                except discord.NotFound as e:
                    print('Message Not Found!')
                    board.valid = False
                    need_save = True
            if need_save:
                self.save_war_data()
        except Exception as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    def create_board(self, war: WarDef, btn=False):
        roster = create_roster_embed(war.roster, war.absent, self, embed=war.embeds(), abrv_line=True)
        ret = {
            'embed': roster,
        }
        if self.config.tag_war:
            ret['content'] = '<@&894698039774679060>'
        if btn:
            ret['components'] = [
                Button(custom_id=f'btn:enlist:{war.id}', label='Signup!'),
                Button(custom_id=f'btn:absent:{war.id}', label='Absent', color='red')
            ]
        return ret

    async def add_war_board(self, war: WarDef, reply_msg=None):
        try:
            if self.config.announce_war:
                if war is not None:
                    channels = self.config.get_notice_channels()
                    for ch in channels:
                        print(ch)
                        if war.can_post(ch):
                            msg: discord.Message = await ch.send(**self.create_board(war, btn=True))
                            war.add_board(msg)
                        else:
                            print('Cannot post!')


        except Exception as e:
            import traceback
            import sys
            traceback.print_exception(*sys.exc_info())

    async def add_war_board_to(self, war: WarDef, ch: discord.TextChannel):
        if war.can_post(ch):
            msg: discord.Message = await ch.send(**self.create_board(war, btn=True))
            war.add_board(msg)
