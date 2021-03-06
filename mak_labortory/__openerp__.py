# -*- coding: utf-8 -*-
##############################################################################
#
#    Mongolyn Alt LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn/, http://asterisk-tech.mn/&gt;). All Rights Reserved
#
#    Email : temuujintsogt@gmail.com
#    Phone : 976 - 99741074
#
##############################################################################
{
    "name" : "MAK Технологи Судалгааны төв",
    "version" : "1.0",
    "author" : "Temuujin",
    "description": """
      MAK Labortory Module
""",
    "website" : False,
    "category" : "MAK",
    "depends" : ['mail','l10n_mn_sale'],
    "init": [],
    "update_xml" : [
        'views/mak_sampler_views.xml',
        'views/mak_lab_sequence.xml',],
    "demo_xml": [],
    'icon': '/logo/static/src/img/mak.png',
    "active": False,
    "installable": True,
    # "auto_install":True,
}