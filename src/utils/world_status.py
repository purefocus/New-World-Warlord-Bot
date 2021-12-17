import requests
from utils.colorprint import *
import discord

import time

BASE_URL = 'https://firstlight.newworldstatus.com/ext/v1/worlds/ohonoo'


class WorldStatus:

    def __init__(self, players_current=-1, players_maximum=-1,
                 queue_current=-1, queue_wait_time_minutes=-1,
                 status_enum=None):
        self.players_current = players_current
        self.players_maximum = players_maximum
        self.queue_current = queue_current
        self.queue_wait_time_minutes = queue_wait_time_minutes
        self.status_enum = status_enum
        self.last_updated = time.strftime('%b %d, %I:%M %p %Z')

        print('World Status:', self)

    def __repr__(self):
        return f'{self.players_current}/{self.players_maximum} ({self.queue_current})'

    def __str__(self):
        return self.__repr__()


def get_status(token) -> WorldStatus:
    sess = requests.Session()
    # print('1')
    header = {
        "Authorization": f'Bearer {token}'
    }
    print_dict(header)
    # print('2')

    result = sess.get(BASE_URL, headers=header)
    # print('3', result.content)
    print(result.text)
    data = result.json()
    # print('data')
    if data['success']:
        return WorldStatus(**data['message'])
    else:
        return WorldStatus(status_enum='Error')

# if __name__ == '__main__':
#     get_status()
