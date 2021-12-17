from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor


class SqlRow:

    def __init__(self):
        self.changed = False

    def finalize(self):
        self.changed = False

    def __setattr__(self, key, value):
        if key != 'changed':
            cur_val = getattr(self, key, None)
            self.changed = self.changed or cur_val != value
        super().__setattr__(key, value)


class SqlTable:

    def __init__(self, db: MySQLConnection, table_name):
        self.table_name = table_name
        self.db = db

    def exec(self, query, params=None) -> MySQLCursor:

        cursor = self.db.cursor()
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        return cursor

    def commit(self):
        self.db.commit()


def get_data_from_cursor(cursor, obj=None):
    rows = cursor.fetchall()
    cols = cursor.column_names
    arr = []
    for row in rows:
        fields = {}
        for i in range(len(cols)):
            fields[cols[i]] = row[i]
        if obj is not None:
            arr.append(obj(**fields))
        else:
            arr.append(fields)
    return arr
