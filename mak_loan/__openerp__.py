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
    "name": "MAK Loan Records",
    "version": "1.0",
    "author": "Temuujin",
    "description": """MAK Loan Management""",
    "website": True,
    "category": "account",
    "depends": ['account','mail'],
    "init": [],
    "update_xml": [
        'views/mak_loan_view.xml',
        'security/mak_loan_sequence.xml',
        'report/mak_loan_report_view.xml',
    ],
    "demo_xml": [
    ],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
}
