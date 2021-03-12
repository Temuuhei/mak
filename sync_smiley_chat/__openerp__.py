# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-Today Synconics Technologies Pvt. Ltd.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

{
    "name": "Smiley Chat",
    "version": "1.0",
    "author": "Synconics Technologies Pvt. Ltd.",
    "website": "www.synconics.com",
    "version": "1.0",
    "catagory": "Social Network",
    "complexity": "easy",
    "summary": "Odoo Smiley Chat",
    "description": """
    This module enables the feature to use smileys while chatting which give more life to chat. You can have smileys to use in individual or group chat to express your emotions which words cannot describe.
    """,
    "depends": ["im_chat"],
	"data": ["views/smiley_chat_view.xml"],
    "qweb": ["static/src/xml/*.xml"],
    "installable": True,
    "auto_install": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
