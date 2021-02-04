# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbat.k@mak.mn
#    Phone : 976 + 99008457
#
##############################################################################

{
    "name": "MAK Economic",
    "version": "1.0",
    "author": "Munkhbat, Bayarbold",
    "description": "Mak economic department calculation",
    "website": True,
    "category": "base",
    "depends": ['mail','calendar'],
    "init": [],
    "data": [
        'security/mak_economic_security.xml',
        'view/mak_economic_view.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
