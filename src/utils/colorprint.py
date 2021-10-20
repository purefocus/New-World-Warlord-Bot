import numpy as np


class TextStyle:

    def __init__(self, code):
        self.num = code
        self.code = f'\x1b[{code}m'

    def __call__(self, *args):
        text = list(args)
        for i in range(len(text)):
            if i > 0 and type(text[i - 1]):
                text[i] = self.code + text[i]
        for i in range(len(text)):
            text[i] = str(text[i])
        return self.code + ''.join(text) + str(colors.reset)

    def __repr__(self):
        return self.code

    def __str__(self):
        return self.code


class TextStyle256(TextStyle):

    def __init__(self, code, fg=True):
        self.num = code
        if fg:
            self.code = f'\x1b[38;5;{code}m'
        else:
            self.code = f'\x1b[48;5;{code}m'


class styles:
    reset = TextStyle(0)
    bold = TextStyle(1)
    light = TextStyle(2)
    italic = TextStyle(3)
    underline = TextStyle(4)
    blink = TextStyle(5)


class colors16:
    reset = TextStyle(0)

    black = TextStyle(30)
    red = TextStyle(31)
    green = TextStyle(32)
    orange = TextStyle(33)
    blue = TextStyle(34)
    magenta = TextStyle(35)
    cyan = TextStyle(36)
    light_grey = TextStyle(37)

    dark_grey = TextStyle(90)
    light_red = TextStyle(91)
    light_green = TextStyle(92)
    yellow = TextStyle(93)
    light_blue = TextStyle(94)
    pink = TextStyle(95)
    light_cyan = TextStyle(96)

    bg_black = TextStyle(40)
    bg_red = TextStyle(41)
    bg_green = TextStyle(42)
    bg_yellow = TextStyle(43)
    bg_blue = TextStyle(44)
    bg_magenta = TextStyle(45)
    bg_cyan = TextStyle(46)
    bg_light_grey = TextStyle(47)


class colors:
    reset = TextStyle256(7)

    black = TextStyle256(0)
    red = TextStyle256(1)
    green = TextStyle256(28)
    orange = TextStyle256(3)
    blue = TextStyle256(4)
    magenta = TextStyle256(5)
    cyan = TextStyle256(6)
    light_grey = TextStyle256(7)

    dark_grey = TextStyle256(8)
    light_red = TextStyle256(9)
    light_green = TextStyle256(10)
    yellow = TextStyle256(11)
    light_blue = TextStyle256(12)
    pink = TextStyle256(13)
    light_cyan = TextStyle256(14)

    purple = TextStyle256(93)
    light_purple = TextStyle256(99)

    bg_black = TextStyle256(0, fg=False)
    bg_red = TextStyle256(1, fg=False)
    bg_green = TextStyle256(2, fg=False)
    bg_yellow = TextStyle256(3, fg=False)
    bg_blue = TextStyle256(4, fg=False)
    bg_magenta = TextStyle256(5, fg=False)
    bg_cyan = TextStyle256(6, fg=False)
    bg_light_grey = TextStyle256(7, fg=False)

    bg_dark_grey = TextStyle256(8, fg=False)
    bg_light_red = TextStyle256(9, fg=False)
    bg_light_green = TextStyle256(10, fg=False)
    bg_yellow = TextStyle256(11, fg=False)
    bg_light_blue = TextStyle256(12, fg=False)
    bg_pink = TextStyle256(13, fg=False)
    bg_light_cyan = TextStyle256(14, fg=False)


name_to_colorcode = {
    'white': colors.black.code,
    'red': colors.red.code,
    'green': colors.green.code,
    'orange': colors.orange.code,
    'blue': colors.blue.code,
    'magenta': colors.magenta.code,
    'cyan': colors.cyan.code,

    'light_grey': colors.light_grey.code,
    'dark_grey': colors.dark_grey.code,
    'light_red': colors.light_red.code,
    'light_green': colors.light_green.code,
    'yellow': colors.yellow.code,
    'light_blue': colors.light_blue.code,
    'pink': colors.pink.code,
    'light_cyan': colors.light_cyan.code,
    'purple': colors.purple.code,
    'light_purple': colors.light_purple.code,
}

colorcode_to_name = {}
for key in name_to_colorcode.keys():
    colorcode_to_name[name_to_colorcode[key]] = key
colorcode_to_name[''] = ''


# print(colorcode_to_name)


def colors_16(color_):
    if color_ % 16 == 0:
        return f"\033[2;{color_}m {color_} \033[0;0m\n"
    return f"\033[2;{color_}m {color_} \033[0;0m"


def colors_256(color_, type=38):
    type = str(type)
    num1 = str(color_)
    num2 = str(color_).ljust(3, ' ')
    if color_ % 16 == 0:
        return (f"\033[{type};5;{num1}m {num2} \033[0;0m\n")
    else:
        return (f"\033[{type};5;{num1}m {num2} \033[0;0m")


def print_color_table():
    print()
    print("The 16 colors scheme is:")
    print(' ' + ' '.join([colors_16(x) for x in range(0, 128)]))
    print("\nThe 256 colors scheme is:")
    print(' ' + ' '.join([colors_256(x) for x in range(256)]))
    print("\nThe 256 colors scheme is:")
    print(' '.join([colors_256(x, type=48) for x in range(256)]))


def cprint(*text):
    print(*text, sep='', end='')


def print_header(*text):
    print(colors.magenta(*text))


def print_value(key, value):
    print(colors.light_blue(key), ': ', colors.light_cyan(value), sep='')


def print_dict(data, info=None):
    if not isinstance(data, dict):
        data = {'data': data}
    if info is not None:
        cprint(colors.orange(info), ': ')
    cprint(styles.light(colors.light_cyan('{\n')))
    print_dict_item(data, ind='\t')
    cprint(colors.light_cyan('}\n'))


def print_dict_item(data: dict, ind=''):
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            value = list(value)
        cprint(ind, styles.light(colors.light_blue(f'\'{key}\'')), ': ')
        if isinstance(value, dict):
            cprint('{\n')
            print_dict_item(value, ind + '\t')
            cprint(ind, '},\n')

        elif isinstance(value, list):

            cprint('[\n')

            for item in value:
                if callable(getattr(item, '__dict__', None)):
                    item = item.__dict__()
                if isinstance(item, dict):
                    cprint(ind + '\t', '{\n')
                    print_dict_item(item, ind + '\t\t')
                    cprint(ind + '\t', '},\n')
                else:
                    cprint(f'{ind}\t', colors.light_green(item), ',\n')

            cprint(f'{ind}],\n')
        elif isinstance(value, Exception):
            cprint(colors.red(str(value)), ',\n')
        else:
            try:
                dct = value.__dict__()
                cprint('{\n')
                print_dict_item(dct, ind + '\t')
                cprint(ind, '},\n')
            except:

                cprint(colors.light_green(value), ',\n')


def print_list(data: list):
    data = list(data)
    cprint('[')
    for i in range(len(data)):
        if i > 0:
            cprint(', ')
        item = data[i]
        if isinstance(item, str):
            cprint('\'', colors.light_purple(item), '\'')
        else:
            cprint(colors.blue(item))
    cprint(']\n')


import re


def strip_colors(input: str):
    input = str(input)
    # s = re.split(r"\033\[[\d+;]*?(\d+)m", input)
    s = re.split(r"(\x1b\[[\d+;]*?[\d+]m)([^\x1b]*)", str(input))
    res = ''
    for i in s:
        if len(i) > 0 and i[0] == '\x1b':
            pass
        else:
            res += i
    # print(s)
    return str(res)


def split_colors(input: str):
    input = str(input)
    s = re.findall(r"(\033\[[\d+;]*?[\d+]m)?([^\033]*)", input)
    res = []
    for color, text in s:
        if len(text) > 0:
            res.append((colorcode_to_name[color], text))
    return res


def print_kv(key, value):
    cprint(colors.light_blue(key), ': ', colors.light_green(value), '\n')


def err(msg):
    print(colors.red(f'Error: \'{str(msg)}\''))
