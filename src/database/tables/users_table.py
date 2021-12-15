from dat.EnlistDef import Enlistment

from mysql.connector import MySQLConnection

_user_data_fields = ['user_id', 'last_updated', 'discord', 'username',
                     'faction', 'company', 'level', 'role', 'weapon1',
                     'weapon2', 'extra', 'edit_key']


class UsersRow:

    def __init__(self):
        self.user_id = None
        self.discord = None
        self.username = None
        self.level = None
        self.role = None
        self.weapon1 = None
        self.weapon2 = None
        self.faction = None
        self.company = None
        self.extra = None
        self.edit_key = None
        self.last_updated = None
        self.changed = False

    def __setattr__(self, key, value):
        if key != 'changed':
            self.changed = True
        super().__setattr__(key, value)

    def __repr__(self):
        return f'{self.discord} [id: {self.user_id}, username: {self.username}, changed: {self.changed}]'


def _data_from_row(row):
    user = UsersRow()
    user.user_id = row[0]
    user.last_updated = row[1]
    user.discord = row[2]
    user.username = row[3]
    user.faction = row[4]
    user.company = row[5]
    user.level = row[6]
    user.role = row[7]
    user.weapon1 = row[8]
    user.weapon2 = row[9]
    user.extra = row[10]
    user.edit_key = row[11]
    user.changed = False
    return user


class TableUsers:

    def __init__(self, table_name, db: MySQLConnection):
        self.table_name = table_name
        self.db = db

        self.users = {}

    def has_user(self, discord_name):
        if discord_name in self.users:
            return True
        return self.get_user(discord_name) is not None

    def get_user(self, name):

        key = 'discord' if '#' in name else 'username'
        query = f'SELECT * FROM users WHERE {key}=%s'

        cursor = self.db.cursor()
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result is None:
            return None
        row = _data_from_row(result)
        self.users[row.discord] = row
        return row

    def insert_user(self, enlist_data: Enlistment):
        query = f'INSERT INTO users (discord, username, faction, company, level, role, weapon1, weapon2, extra, edit_key) ' \
                f'VALUES (%(discord)s, %(username)s, %(faction)s, %(company)s, ' \
                f'%(level)s, %(role)s, %(weapon1)s, %(weapon2)s, %(extra)s, %(edit_key)s) ' \
                f'ON DUPLICATE KEY update user_id=user_id;'

        cursor = self.db.cursor()
        cursor.execute(query, enlist_data.table_data())
        self.db.commit()
        user = self.get_user(enlist_data.disc_name)

        return user

    def get_users(self, discord=None, username=None, company=None, faction=None, role=None, weapons=None):
        where = '1 '
        params = []
        if discord is not None:
            where += f"AND discord LIKE '%%s%' "
            params.append(discord)
        if username is not None:
            where += f"AND username LIKE '%%s%' "
            params.append(username)
        if company is not None:
            where += f"AND company LIKE '%%s%' "
            params.append(company)
        if faction is not None:
            where += f"AND faction LIKE '%%s%' "
            params.append(faction)
        if role is not None:
            where += f"AND role LIKE '%%s%' "
            params.append(role)
        if weapons is not None:
            if isinstance(weapons, str):
                weapons = [weapons]
            for w in weapons:
                where += f"AND (weapon1 LIKE '%%s%' OR weapon2 LIKE '%%s%' "
                params.append(w)
                params.append(w)

        query = f'SELECT * FROM users WHERE {where};'
        cursor = self.db.cursor()
        cursor.execute(query, params)

        results = cursor.fetchall()
