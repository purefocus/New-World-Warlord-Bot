from dat.EnlistDef import Enlistment

import requests
from utils.colorprint import print_dict

FORM_URL1 = 'https://docs.google.com/forms/u/2/d/e/1FAIpQLSfYNr3uLqLKoXKuY6PmHsugpEn4H6QjL84dY6-KgDabq_gGtA/viewform?usp=form_confirm&amp;edit2='
FORM_URL = 'https://docs.google.com/forms/u/2/d/e/1FAIpQLSfYNr3uLqLKoXKuY6PmHsugpEn4H6QjL84dY6-KgDabq_gGtA/formResponse'

EDIT_2 = '2_ABaOnudWIcmscEsShG8bWWtJKZsFF9FdvSOQ3MxWo6KmHb10jQjEJf2UI54p6BfMzgAPpv4'

import re

field2post = {
    'username': 820633411,
    'company': 1177546279,
    'level': 1402936126,
    'gearscore': 983521405,
    'primary_weapon': 107020616,
    'secondary_weapon': 306341460,
    'preferred_group': 74838911,
    'faction': 324917347,
    'role': 184378169,
}


def post_enlistment(enl: Enlistment):
    try:
        data = enl.data()
        fields = ['username', 'level', 'role', 'primary_weapon', 'secondary_weapon', 'preferred_group', 'company',
                  'faction']
        # self.username,
        # self.level,
        # role,
        # weapons[0],
        # weapons[1],
        # self.group,
        # self.company,
        # self.faction

        req = {
            "fvv": 1, "partialResponse": '[]', "pageHistory": 0, "fbzx": -6893020537148369068
        }
        for i in range(len(fields)):
            dat = str(data[i])
            post_key = field2post[fields[i]]
            # if dat is None:
            #     req[post_key] = None
            # else:
            req[f'entry.{post_key}'] = str(dat)  # .replace(' ', '+')

        params = {}
        if enl.edit_key is not None:
            params['edit2'] = enl.edit_key

        response = requests.post(url=FORM_URL, data=req, params=params)
        content = str(response.content, 'UTF-8')
        regex = re.compile('<a href=\".*edit2=(.*)\">Edit your response</a>')
        match = regex.findall(content)
        if len(match) > 0:
            print(match[0])
            enl.edit_key = match[0]
    except Exception as e:
        import traceback
        import sys
        traceback.print_exception(*sys.exc_info())


if __name__ == '__main__':

    from utils.userdata import UserData

    users = UserData()
    users.load('../../files/user_data.json')
    for user in users.users:
        user = users[user]
        post_enlistment(user)
    users.save('../../files/user_data2.json')
