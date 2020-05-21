# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-today MNO LLC (<http://www.mno.mn>)
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
    'name' : 'HSE',
    'version' : '0.1',
    'author' : 'Tr1um',
    'website' : 'http://www.mak.mn/',
    'category' : 'Hse',
    'description': 'Mongolian mining operator company',
    'depends' : ['base','mail','hr','l10n_mn_mining','l10n_mn_hr_training'],
    'data'   :  [
                 'security/hse_security.xml',
                 'security/ir.model.access.csv',
                 'hse_view.xml',
                 'report/hse_report_view.xml',
                 'report/hse_my_safety_view.xml',
                 'report/hse_report_analyze_view.xml',
                 'report/hse_safety_report_view.xml',
                 'views/hse.xml',
                 'wizard/hse_document.xml',
                 'wizard/hse_report_injury_pdf.xml',
                 'menu_view.xml',
    ],
    'init_xml' : [ ],
    'demo_xml' : [ ],
    'update_xml' : [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'qweb': ['static/src/xml/hse_xml.xml',
    'static/src/xml/hse_report_xml.xml',
    'static/src/xml/hse_injury_image.xml',
    'static/src/xml/hse_cor_act_injury_image.xml',
    'static/src/xml/hse_desc_injury_image.xml',
    'static/src/xml/hse_safety_report.xml',
    'static/src/xml/hse_corrective_actions.xml',
    'static/src/xml/hse_my_safety.xml'],
}