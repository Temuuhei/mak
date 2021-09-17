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
    "name": "MAK IT Helpdesk",
    "version": "1.0",
    "author": "Munkhbat",
    "description": "MAK IT Helpdesk",
    "website": True,
    "category": "base",
    "depends": ['mail', 'calendar'],
    "init": [],
    "data": [
        'security/mak_it_helpdesk_security.xml',
        "security/ir.model.access.csv",
        'view/mak_it_helpdesk_view.xml',
        'view/mak_erp_dev_helpdesk_view.xml',
        'wizard/migrate_to_it_helpdesk.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
