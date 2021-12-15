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

from database.tables.users_table import TableUsers


class SqlDatabase:

    def __init__(self, cfg):
        mysql_cfg = cfg.mysql_cfg

        print(f'Connecting to MySQL...  ', end='')

        if mysql_cfg['tunnel']:
            tunnel = SSHTunnelForwarder(('52.188.110.43', 22),
                                        ssh_username=mysql_cfg['ssh_username'],
                                        ssh_password=mysql_cfg['ssh_password'],
                                        remote_bind_address=('127.0.0.1', mysql_cfg['port']))
            tunnel.start()
            self.db = mcon.connect(host=tunnel.local_bind_host,
                                   user=mysql_cfg['username'],
                                   password=mysql_cfg['password'],
                                   database=mysql_cfg['database'],
                                   port=tunnel.local_bind_port,
                                   use_pure=True)
        else:
            self.db = mcon.connect(host=mysql_cfg['host'],
                                   user=mysql_cfg['username'],
                                   password=mysql_cfg['password'],
                                   database=mysql_cfg['database'],
                                   port=mysql_cfg['port'],
                                   charset='utf8mb4',
                                   use_pure=True)
        self.db.set_unicode(True)

        if (self.db.is_connected()):
            print('Connected!')
        else:
            print('Connection Failed!')

        self.users = TableUsers('users', self.db)
