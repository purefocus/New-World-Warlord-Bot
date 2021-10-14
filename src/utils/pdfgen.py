from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from config import tmpfile
from dat.WarDef import *


def generate_enlistment_pdf(war: WarDef):
    file = tmpfile('roster.pdf')
    document = SimpleDocTemplate(file, pagesize=A4)
    data = war.create_table()

    table = Table(data)
    table.setStyle(TableStyle(
        [
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
    ))
    contents = [
        table,
    ]

    document.build(contents)
    return file
