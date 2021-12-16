import discord
from dat.UserSignup import *
from dat.EnlistDef import *
from dat.GroupAssignments import *

from utils.data import *

import uuid
from utils.details import WAR_ROLES
from utils.details import parse_date

from database.tables.users_table import UserRow
from database.tables.sql_table import *


class MsgFunc:
    Status_Status = 'Status_Status'
    Status_Players = 'Status_Players'
    Status_Queue = 'Status_Queue'
    ServerStatus = 'ServerStatus'
    War = 'War'


class MsgRow(SqlRow):

    def __init__(self, id=-1, gid=None, cid=None, mid=None, func=None, info=None, valid=False):
        super().__init__()
        self.id = id
        self.gid = gid
        self.cid = cid
        self.mid = mid
        self.func = func
        self.info = info
        self.valid = valid

    async def resolve(self, client: discord.Client) -> [discord.Message, discord.VoiceChannel]:
        guild = client.get_guild(self.gid)
        if guild != None:
            channel = guild.get_channel(self.cid)
            if self.mid != -1:
                return await channel.fetch_message(self.mid)
            else:
                return channel
        return None


class MessagesTable(SqlTable):

    def __init__(self, db: MySQLConnection, table_name):
        super().__init__(db, table_name)

    def add_message(self, m: MsgRow):
        query = f'INSERT INTO {self.table_name} (gid, cid, mid, func, info, valid) VALUES (%s, %s, %s, %s, %s, %s);'

        cursor = self.exec(query, (m.gid, m.cid, m.mid, m.func, m.info, m.valid))
        m.id = cursor.getlastrowid()
        self.commit()
        return m

    def invalidate(self, m: MsgRow):
        if m.id == -1:
            return
        query = f'UPDATE {self.table_name} SET valid=0 WHERE id={m.id};'
        self.exec(query)
        self.commit()

    def get_messages(self, id=None, gid=None, cid=None, mid=None, func=None, info=None, valid=None):
        where = '1 '
        params = []
        if id is not None:
            where += f"AND id = %s "
            params.append(id)
        if gid is not None:
            where += f"AND gid = %s "
            params.append(gid)
        if cid is not None:
            where += f"AND cid = %s "
            params.append(cid)
        if mid is not None:
            where += f"AND mid = %s "
            params.append(mid)
        if func is not None:
            where += f"AND func = %s "
            params.append(func)
        if info is not None:
            where += f"AND info = %s "
            params.append(info)
        if valid is not None:
            where += f"AND valid = %s "
            params.append(valid)

        query = f'SELECT * FROM {self.table_name} WHERE {where};'

        cursor = self.exec(query, (params))
        rows = get_data_from_cursor(cursor, MsgRow)
        print(rows)
        return rows
