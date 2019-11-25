# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : temuujin.ts@mak.mn
#    Phone : 976 + 99741074
#
##############################################################################

{
    "name": "MAK Reminder",
    "version": "1.0",
    "author": "Temuujin",
    "description": """Mak reminder that inherited  by calendar""",
    "website": True,
    "category": "base",
    "depends": ['calendar','mail'],
    "init": [],
    "data": [
        'mak_calendar_view.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
