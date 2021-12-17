from database.tables.sql_table import *
from database.tables.users_table import UserRow


class WarRow(SqlRow):

    def __init__(self, id=None, uuid=None, active=False, private=None,
                 name=None, owners=None, attacking=None,
                 defending=None, location=None, created=None,
                 wartime=None, image=None, extra=None):
        super().__init__()
        self.id = id
        self.uuid = uuid
        self.active = active
        self.private = private
        self.name = name
        self.owners = owners
        self.attacking = attacking
        self.defending = defending
        self.location = location
        self.created = created
        self.wartime = wartime
        self.image = image
        self.extra = extra

        self.roster = []
        self.absent = []


class WarTable(SqlTable):

    def __init__(self, db: MySQLConnection, table_name):
        super().__init__(db, table_name)
        self.wars = {}

    def add_war(self, war: WarRow):

        query = f'INSERT INTO {self.table_name} (uuid, owners, private, active, name, attacking, defending, location, wartime, image, extra)' \
                f'VALUES (%(uuid)s, %(owners)s, %(private)s, %(active)s, %(name)s, %(attacking)s, %(defending)s, %(location)s, TIMESTAMP(%(wartime)s), %(image)s, %(extra)s) ON DUPLICATE KEY UPDATE id=id;'

        params = {
            'id': war.id,
            'uuid': war.uuid,
            'active': war.active,
            'private': war.private,
            'name': war.name,
            'owners': war.owners,
            'attacking': war.attacking,
            'defending': war.defending,
            'location': war.location,
            'created': war.created,
            'wartime': war.wartime,
            'image': war.image,
            'extra': war.extra
        }
        cursor = self.exec(query, params)
        id = cursor.getlastrowid()
        if id > 0:
            war.id = cursor.getlastrowid()
        self.commit()
        war.changed = False

    def update_war(self, war: WarRow):
        # if war.changed:
        query = f'UPDATE {self.table_name} SET ' \
                f'owners=%(owners)s, active=%(active)s, name=%(name)s, attacking=%(attacking)s, ' \
                f'defending=%(defending)s, location=%(location)s, wartime=TIMESTAMP(%(wartime)s), image=%(image)s, extra=%(extra)s ' \
                f'WHERE uuid=%(uuid)s;'

        params = {
            'uuid': war.uuid,
            'active': war.active,
            'name': war.name,
            'owners': war.owners,
            'attacking': war.attacking,
            'defending': war.defending,
            'location': war.location,
            'wartime': war.wartime,
            'image': war.image,
            'extra': war.extra
        }
        cursor = self.exec(query, params)
        id = cursor.getlastrowid()
        if id > 0:
            war.id = cursor.getlastrowid()
        self.commit()

        war.changed = False

    def get_active_wars(self):
        query = f'SELECT * FROM {self.table_name} WHERE active=1;'

        cursor = self.exec(query)
        result = get_data_from_cursor(cursor, WarRow)

        self.wars = {}
        for war in result:
            war: WarRow = war
            self.wars[war.uuid] = war

        return self.wars

    def get_war(self, uuid):
        query = f'SELECT * FROM {self.table_name} WHERE uuid=%s;'

        cursor = self.exec(query, (uuid,))
        result = get_data_from_cursor(cursor, WarRow)
        if len(result) == 0:
            return None
        for war in result:
            war: WarRow = war
            self.wars[war.uuid] = war
            return war
        # return war

    def get_roster_for(self, war: WarRow):
        query = f'SELECT `users`.`discord` AS `user`, `roster`.`enlist` FROM `roster` ' \
                f'INNER JOIN `users` ON `users`.user_id = `roster`.user_id WHERE `roster`.event_id = %s;'

        cursor = self.exec(query, (war.id,))
        war.roster = []
        war.absent = []

        rows = get_data_from_cursor(cursor)
        for row in rows:
            if row['enlist']:
                war.roster.append(row['user'])
            else:
                war.absent.append(row['user'])

        return war.roster

    def remove_enlistment(self, user: UserRow, war: WarRow):
        query = f'DELETE FROM roster WHERE user_id=%s AND event_id=%s;'
        self.exec(query, (user.user_id, war.id))

    def enlist_user(self, user: UserRow, war: WarRow, absent=False):
        try:
            self.remove_enlistment(user, war)
            query = f'INSERT INTO `roster` (user_id, event_id, enlist) VALUES (%s, %s, %s);'

            self.exec(query, (user.user_id, war.id, not absent))
        except Exception as e:
            print(f'Error (enlist_user({user}, {war}) ->', str(e))

    def enlisted_in(self, user: UserRow):
        try:
            query = f'SELECT wars.id, wars.uuid, wars.name FROM wars INNER JOIN roster ON wars.id = roster.event_id WHERE roster.user_id = %s AND wars.active=1;'
            cursor = self.exec(query, (user.user_id,))

            rows = get_data_from_cursor(cursor)
            return rows
        except Exception as e:
            print(f'Error (enlisted_in({user})) ->', str(e))

        return []

    def resolve_war(self, key):
        if key in self.wars:
            return self.wars[key]

        for war in self.wars:
            war = self.wars[war]
            if str(war.id) == str(key):
                return war
        return None

    def __getitem__(self, uuid) -> [None, WarRow]:
        try:
            if uuid in self.wars:
                return self.wars[uuid]
            else:
                return self.get_war(uuid)
        except:
            pass
        return None

    def __setitem__(self, uuid, war):
        try:
            self.update_war(war)
            if uuid in self.wars:
                self.wars[uuid] = war
        except:
            pass
        return None

    def update_changed(self):
        for war in self.wars:
            war: WarRow = self.wars[war]
            self.update_war(war)
