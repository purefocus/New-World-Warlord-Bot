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
    'primary weapon': 107020616,
    'secondary weapon': 306341460,
    'preferred group': 74838911,
    'faction': 324917347,
    'role': 184378169,
}


def post_enlistment(enl: Enlistment):
    try:
        data = enl.data()
        fields = ['username', 'level', 'role', 'primary weapon', 'secondary weapon', 'preferred group', 'company',
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
            dat = data[i]
            post_key = field2post[fields[i]]
            if dat is None or dat == 'none':
                dat = ''
            req[f'entry.{post_key}'] = dat

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


def _process_html(inp):
    inp = str(inp, 'UTF-8')
    inp = inp.replace('&quot;', '\"')
    inp = inp.replace('\\u003c', '<').replace('\\u003e', '>')
    inp = inp.replace('<div', '\n<div')
    return inp


def parse_google_form(url: str):
    sess = requests.Session()
    form = sess.get(url, params={'usp': 'sf_link'})
    regex = r'data-params="%\.@\.\[[0-9]*,"(?P<name>[\w ]*)",(?P<desc>".*?"|null),[0-9],\[\[(?P<entry_id>[0-9]*)'
    choices_regex = r'\["(.*?)",null,null,null,\w*\]'
    matcher = re.compile(regex)
    choices_matcher = re.compile(choices_regex)
    content = _process_html(form.content)
    # print(content)
    # print('Matched: ', matcher.search(content))
    dict = {}
    for name, desc, code in matcher.findall(content):
        print(f'Name: {name}, desc: {desc}, code: {code}')
        dict[name.lower()] = code
    print_dict(dict)


if __name__ == '__main__':
    parse_google_form(
        'https://docs.google.com/forms/d/e/1FAIpQLSfYNr3uLqLKoXKuY6PmHsugpEn4H6QjL84dY6-KgDabq_gGtA/viewform?usp=sf_link')

    # from utils.userdata import UserData
    #
    # users = UserData()
    # users.load('../../files/user_data.json')
    # for user in users.users:
    #     user = users[user]
    #     post_enlistment(user)
    # users.save('../../files/user_data2.json')
