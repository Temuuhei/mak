# -*- encoding: utf-8 -*-
##############################################################################
#
#    Samples module for Odoo 8 Backend Theme
#    Copyright (c) 2015 Antiun Ingeniería S.L. (http://www.antiun.com)
#       Endika Iglesias <endikaig@antiun.com>
#       Antonio Espinosa <antonioea@antiun.com>
#       Daniel Góme-Zurita <danielgz@antiun.com>
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
    # Module information
    'name': 'Blue Backend Theme V8',
    'version': '1.0',
    'category': 'Themes/Backend',

    # Your information
    'author': 'MinhHQ',
    'website': 'https://www.linkedin.com/in/minh-hong-350971109/',
    'license': 'AGPL-3',
    'summary': 'Blue Backend Theme V8',
    'images': [
        'images/screen.png'
    ],

    # Dependencies
    'depends': [
        'web',
    ],

    # Views templates, pages, menus, options and snippets
    'data': [
        'views/backend.xml',
    ],

    # Qweb templates
    'qweb': [
        'static/src/xml/backend.xml',
    ],

    # Technical options
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
