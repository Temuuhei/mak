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
    "name": "MAK - HR Regulations",
    "version": "1.0",
    "author": "Temuujin",
    "description": """Human Resource Regulations""",
    "website": True,
    "category": "base",
    "depends": ['hr','mail','l10n_mn_hr_regulation'],
    "init": [],
    "update_xml": [
        'email_template/mak_reg_email_template_to_assigned.xml',
        'email_template/mak_reg_email_template_user.xml',
        'security/mak_regulation_sequence.xml',
        'views/mak_regulation_view.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
