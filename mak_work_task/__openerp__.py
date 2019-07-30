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
    "name": "MAK - Work Task Management",
    "version": "1.0",
    "author": "Temuujin",
    "description": """Task Management for Law department""",
    "website": True,
    "category": "base",
    "depends": ['mail','l10n_mn_contract_management','l10n_mn_mak_contract_management'],
    "init": [],
    "update_xml": [
        'email_template/task_email_template_to_assigned.xml',
        'security/task_management_security.xml',
        'views/task_management_view.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
