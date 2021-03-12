# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbaat.k@mak.mn & bayarbold.b@mak.mn
#    Phone : 976 + 99741074
#
##############################################################################

{
    "name": "MAK Economic Calculation",
    "version": "1.0",
    "author": "MB and BB",
    "description": """Mak calculation record for economic department""",
    "website": True,
    "category": "base",
    "depends": ['hr','mail'],
    "init": [],
    "data": [
        'views/mak_economic_view.xml',

    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
