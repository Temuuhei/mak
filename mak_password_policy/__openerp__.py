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
    "name" : "MAK - Password Policy",
    "version" : "1.0",
    "author" : "Temuujin",
    "description": """Password Policy""",
    "website" : True,
    "category" : "base",
    "depends" : ['base',],
    "init": [],
    "update_xml" : [
        'security/password_reset_security.xml',          
         
    ],
    "demo_xml": [
    ],
    'icon': '/logo/static/src/img/mak.png',
    "active": False,
    "installable": True,
}
