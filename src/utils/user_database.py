import mysql.connector as mcon

_user_data_fields = ['username', 'discord', 'faction', 'company', 'level', 'role', 'primary_weapon', 'secondary_weapon',
                     'extra_information', 'edit_key', 'last_updated']
'''
(' \
                f'%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                
                '''


class UserDatabase:

    def __init__(self, cfg):
        login = cfg.mysql_login

        self.mydb = mcon.connect(host='localhost', user=login['username'], password=login['password'],
                                 database='warlord')

    def add_user(self, user):
        data = user.data()
        values = [data[0], user.disc_name, data[7], data[6], data[1], data[2],
                  data[3], data[4], data[5], user.edit_key, 'NOW()']
        query = f'INSERT INTO UserData ({", ".join(_user_data_fields)}) VALUES ({", ".join(values)})'

        cursor = self.mydb.cursor()
        cursor.execute(query, values)
        self.mydb.commit()

        print(cursor.rowcount, "Record Inserted")

    def get_user(self, user):
        pass
