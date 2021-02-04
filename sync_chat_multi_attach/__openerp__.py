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
    "name": "Chat Multi Attachments", 
    "version": "1.0", 
    'author': 'Synconics Technologies Pvt. Ltd.',
    'website': 'https://www.synconics.com',
    "category": "Social Network",
    "summary": "Drag & Drop multiple attachments in the chat at once",
    "description": """
    This module enables the feature to send multiple attachments to individual or group of recipient in the chat at once.
    
    There are two ways to send files in the chat, this will benefit you to transfer files to those who are the members of that particular chat group.
    
    First Way: Through attachment button, it will lead you to the file browser - from where you can select more than one file and click on "Open" button. The attached files will send in group/individual chat as it is posted.
    
    Second Way: To send files in the chat, You have to explore the file(s), select the file(s) and drag & drop them into the "Drop your files here" area of the chat window.

    Installation Requirements:
    ==========================
    
    To install this module, make sure you have installed "sync_mail_multi_attach" dependency module.
    
    Download Link: https://www.odoo.com/apps/modules/8.0/sync_mail_multi_attach/
    """,
    "depends": ["document", "sync_mail_multi_attach"],
    'data': ["views/chat_multi_attach.xml"],
    'qweb': ['static/src/xml/*.xml'],
    "price": 20,
    "currency": "EUR", 
    "installable": True, 
    "auto_install": False
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
