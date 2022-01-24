from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from config import tmpfile
from dat.WarDef import *

import pandas as pd


def generate_enlistment_pdf(war: WarDef, users):
    file = tmpfile('roster.pdf')
    document = SimpleDocTemplate(file, pagesize=A4)
    data = war.create_table(users)

    data = sorted(data, key=lambda x: x.sort_key(), reverse=True)

    table_data = [['Name', 'Role', 'Weapons', 'Company']]
    for dat in data:
        row = dat.make_table_row()
        table_data.append(row)

    style_data = [
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),  # grid lines inside table
        # ('ALIGN', (0, 0), (-1, 0), 'CENTER'),  # header row
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # user_id column
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),  # level column
        ('ALIGN', (-1, 0), (-1, -1), 'LEFT'),  # roles column

        ('FONT', (0, 0), (-1, 0), 'Times-Bold'),  # header row
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),  # Thicker grid lines for the header
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.black),  # row grid lines for all cells
    ]

    last_role = table_data[0][1]
    for i in range(1, len(table_data)):
        if last_role != table_data[i][1]:
            last_role = table_data[i][1]
            style_data.append(('LINEBELOW', (0, i - 1), (-1, i - 1), 1.5, colors.black))

    table = Table(table_data)
    table.setStyle(TableStyle(style_data))
    contents = [
        table,
    ]

    document.build(contents)
    return file


def generate_enlistment_pandas(war: WarDef, users):
    data = war.create_table(users)

    data = sorted(data, key=lambda x: str(x[1].role) + str(x[1].company) + str(x[1].level), reverse=True)
    dat = []
    for enl, entry in data:

        d = [entry.username, entry.level, entry.role, entry.weight, entry.weapon1, entry.weapon2, entry.extra,
             entry.company,
             entry.faction]
        if not enl:
            d[2:] = ['ABSENT', '', '', '', '', '', '']
        dat.append(d)
    data = dat  # [entry.data() for enl, entry in data]

    data = pd.DataFrame(data,
                        columns=[
                            'Name',
                            'Level',
                            'Role',
                            'Weight',
                            'Primary Weapon',
                            'Secondary Weapon',
                            'Preferred Group',
                            'Company',
                            'Faction',
                        ])

    return data


def generate_enlistment_csv(war: WarDef, users):
    file = tmpfile('roster.csv')

    data = generate_enlistment_pandas(war, users)

    # table_data = [['Name', 'Role', 'Weapons', 'Company']]
    data.to_csv(file, index=True, header=True)
    print('data Saved!')
    return file


def generate_enlistment_excel(war: WarDef, users):
    file = tmpfile('roster.xlsx')

    data = generate_enlistment_pandas(war, users)

    data.to_excel(file, index=True, header=True)
    return file
