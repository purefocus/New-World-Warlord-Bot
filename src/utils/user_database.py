import json

import config as cfg
from dat.EnlistDef import Enlistment
from utils.google_forms import post_enlistment
import mysql.connector as mcon

import paramiko
from paramiko import SSHClient
from sshtunnel import SSHTunnelForwarder
from utils.colorprint import *
from utils.dbutil import *

_user_data_fields = ['username', 'discord', 'faction', 'company', 'level', 'role', 'primary_weapon', 'secondary_weapon',
                     'extra_information', 'edit_key', 'last_updated']
'''
(' \
                f'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                
                '''


class UserDatabase:

    def __init__(self, cfg):
        mysql_cfg = cfg.mysql_cfg

        print(f'Connecting to MySQL...  ', end='')

        if mysql_cfg['tunnel']:
            tunnel = SSHTunnelForwarder(('52.188.110.43', 22),
                                        ssh_username=mysql_cfg['ssh_username'],
                                        ssh_password=mysql_cfg['ssh_password'],
                                        remote_bind_address=('127.0.0.1', mysql_cfg['port']))
            tunnel.start()
            self.mydb = mcon.connect(host=tunnel.local_bind_host,
                                     user=mysql_cfg['username'],
                                     password=mysql_cfg['password'],
                                     database=mysql_cfg['database'],
                                     port=tunnel.local_bind_port,
                                     use_pure=True)
        else:
            self.mydb = mcon.connect(host=mysql_cfg['host'],
                                     user=mysql_cfg['username'],
                                     password=mysql_cfg['password'],
                                     database=mysql_cfg['database'],
                                     port=mysql_cfg['port'],
                                     use_pure=True)
        self.mydb.set_unicode(True)

        if (self.mydb.is_connected()):
            print('Connected!')
        else:
            print('Connection Failed!')

    def add_user(self, user):
        try:
            enl = self.get_user(user)
            if enl is not None:
                self.update_user(enl)
                return

            data = user.data()
            entry = {
                'username': data[0],
                'discord': user.disc_name,
                'faction': data[7],
                'company': data[6],
                'level': data[1],
                'role': data[2],
                'weapon1': data[3],
                'weapon2': data[4],
                'extra': data[5],
                'edit_key': user.edit_key,
            }

            query, param = insert_query('users', entry, dup_update=True)
            cursor = self.mydb.cursor()

            cursor.execute(query, param)
            self.mydb.commit()

            # print(cursor.rowcount, "Record Inserted")
        except:
            print('Failed to add user!')
            print(user.data())

    def update_user(self, user):
        data = user.data()

        entry = {
            'faction': data[7],
            'company': data[6],
            'level': data[1],
            'role': data[2],
            'weapon1': data[3],
            'weapon2': data[4],
            'extra': data[5],
            'edit_key': user.edit_key,
        }

        query, param = update_query('users', entry, {'discord': user.disc_name})
        cursor = self.mydb.cursor()

        cursor.execute(query, param)
        self.mydb.commit()

    def get_user(self, user):
        entry = {
            'discord': user.disc_name
        }
        query, param = select_query('users', entry)

        cursor = self.mydb.cursor()

        cursor.execute(query, param)

        result = cursor.fetchall()
        if len(result) == 0:
            return None

        return self._row_to_user(result[0])

    # def get_all_users(self):

    def _row_to_user(self, row: tuple):
        id, discord, username, level, role, w1, w2, faction, company, extra, edit_key, last_updated = row
        enl = Enlistment(disc_name=discord, username=username, level=level, faction=faction, company=company,
                         group=extra,
                         roles={
                             role: f'{w1}/{w2}'
                         },
                         edit_key=edit_key)
        return enl
