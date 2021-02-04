# -*- coding: utf-8 -*-
##############################################################################
#
#    Asterisk Technologies LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn/, http://asterisk-tech.mn/&gt;). All Rights Reserved
#
#    Email : info@asterisk-tech.mn
#    Phone : 976 + 88005462, 976 + 94100149
#
##############################################################################
{
    "name" : "MAK Data delete tool",
    "version" : "1.0",
    "author" : "Temuujin",
    "description": """
      MAK  Old Data tool when old data is unuseful
""",
    "website" : False,
    "category" : "Product",
    "depends" : ['product'],
    "init": [],
    "update_xml" : [
               'views/product_inherit_view.xml',
                'security/old_data_delete_security.xml',

             ],
    "demo_xml": [],
    'icon': '/logo/mak.png',
    "active": False,
    "installable": True,
    # "auto_install":True,
}