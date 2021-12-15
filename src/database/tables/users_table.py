from dat.EnlistDef import Enlistment

from mysql.connector import MySQLConnection

_user_data_fields = ['user_id', 'last_updated', 'discord', 'username',
                     'faction', 'company', 'level', 'role', 'weapon1',
                     'weapon2', 'extra', 'edit_key']


class UsersRow:

    def __init__(self, discord=None, username=None, level=None,
                 role=None, weapon1=None, weapon2=None,
                 faction=None, company=None, extra=None,
                 edit_key=None, last_updated=None):
        self.user_id = -1
        self.discord = discord
        self.username = username
        self.level = level
        self.role = role
        self.weapon1 = weapon1
        self.weapon2 = weapon2
        self.faction = faction
        self.company = company
        self.extra = extra
        self.edit_key = edit_key
        self.last_updated = last_updated
        self.changed = False

    def __setattr__(self, key, value):
        if key != 'changed':
            self.changed = True
        super().__setattr__(key, value)

    def __repr__(self):
        return f'{self.discord} [id: {self.user_id}, username: {self.username}, changed: {self.changed}]'

    def to_enlistment(self):
        enl = Enlistment(disc_name=self.discord, username=self.username, level=self.level,
                         faction=self.faction, company=self.company, group=self.extra,
                         roles={self.role: f'{self.weapon1}/{self.weapon2}'}, edit_key=self.edit_key)
        return enl


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
        self.name_to_disc_map = {}

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

    def update_row(self, user: UsersRow):
        if user.changed:
            query = f'UPDATE users SET ' \
                    f'company=%s, level=%s, role=%s, weapon1=%s, weapon2=%s, extra=%s, edit_key=%s ' \
                    f'WHERE user_id=%s;'

            cursor = self.db.cursor()
            cursor.execute(query,
                           (user.company, user.level, user.role, user.weapon1, user.weapon2, user.extra, user.edit_key,
                            user.user_id))
            self.db.commit()
            user.changed = False
            return True
        return False

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
            where += f"AND discord LIKE %s "
            params.append(f'%{discord}%')
        if username is not None:
            where += f"AND username LIKE %s "
            params.append(f'%{username}%')
        if company is not None:
            where += f"AND company LIKE %s "
            params.append(f'%{company}%')
        if faction is not None:
            where += f"AND faction LIKE %s "
            params.append(f'%{faction}%')
        if role is not None:
            where += f"AND role LIKE %s "
            params.append(f'%{role}%')
        if weapons is not None:
            if isinstance(weapons, str):
                weapons = [weapons]
            for w in weapons:
                where += f"AND (weapon1 LIKE '%s' OR weapon2 LIKE '%s')"
                params.append(f'%{w}%')
                params.append(f'%{w}%')

        query = f'SELECT * FROM users WHERE {where};'
        cursor = self.db.cursor()
        cursor.execute(query, params)

        users = []
        results = cursor.fetchall()
        for result in results:
            user = _data_from_row(result)
            users.append(user)
            self.users[user.discord] = user

        return users

    def update_changed(self):
        for user in self.users:
            user: UsersRow = self.users[user]
            self.update_row(user)


    def add_user(self, disc_name, user: Enlistment):
        user.disc_name = disc_name
        if disc_name in self.users:
            u: UsersRow = self.users[disc_name]
            data = user.table_data()
            u.role = data['role']
            u.weapon1 = data['weapon1']
            u.weapon2 = data['weapon2']
            u.extra = data['extra']
            u.faction = data['faction']
            u.company = data['company']
            u.level = data['level']
            u.edit_key = u.edit_key
            self.update_row(u)
        self.insert_user(user)
        # self.users[disc_name] = user
        self.name_to_disc_map[user.username.lower()] = disc_name

    def load(self, file=None):
        try:
            self.get_users()
        except Exception as e:
            print(e)

    def save(self, file=None):
        try:
            self.update_changed()
        except Exception as e:
            print(e)

    def __getitem__(self, name) -> [None, Enlistment]:
        try:
            # name = name.lower()
            if '#' not in name:
                name = self.name_to_disc_map[name.lower()]
                # name = name.lower()
            if name in self.users:
                return self.users[name].to_enlistment()
        except:
            pass
        return None

    def __contains__(self, item):
        if isinstance(item, str):
            item = item.lower()
            if '#' not in item:
                item = self.name_to_disc_map[item]
            return item in self.users
        return False

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'Enlisted: {len(self.users)}'
