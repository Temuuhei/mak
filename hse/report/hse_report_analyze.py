# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp import tools
from datetime import datetime, timedelta

class report_hse_injury_entry(osv.osv):
    _name = 'report.hse.injury.entry'
    _description = 'Injury entry'
    _auto = False
    _columns = {
        'datetime': fields.datetime('Datetime', readonly=True),
        # 'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        # 'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        # 'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        # 'state': fields.selection([('draft', 'Draft'),('sent_mail', 'Sent to mail'),('closed', 'Closed'),('cor_act_closed', 'Corrective actions closed')], 'State', readonly=True),
        'name': fields.char('Number', size=20, readonly=True),
        'accident_name': fields.char('Accident name', size=200, readonly=True),
        # 'technic_ids': fields.many2many('asset.technic.passpord', 'hse_injury_entry_technic_rel','injury_id', 'technic_id', 'Technic'),
        'lost_day': fields.integer('Lost day'),
        # 'involved_employee': fields.many2many('hr.employee', 'hse_injury_entry_involved_employee_rel','injury_id', 'employee_id', 'Involved employee'),
        'project_id': fields.many2one('project.project','Project', readonly=True),
        'department_id': fields.many2one('hr.department','Department', readonly=True),
        'project_manager_id': fields.many2one('hr.employee','Project manager', readonly=True),
        'dep_manager_id': fields.many2one('hr.employee','Department manager', readonly=True),
        'general_master_id': fields.many2one('hr.employee','General master', readonly=True),
        'master_id': fields.many2one('hr.employee','Master', readonly=True),
        
        'accident_type': fields.many2one('hse.accident.type', 'Accident type', readonly=True),
        # 'value': fields.related('accident_type','value', type='char', relation='hse.accident.cause', store=True, string='Value'),

        'location_accident': fields.char('The location of the accident', size=100, readonly=True),
        'consequence_id': fields.many2one('hse.consequence', 'Potential significance', readonly=True),
        'likelihood_id': fields.many2one('hse.likelihood', 'Likelihood reoccure',readonly=True),
        # 'before_injury': fields.text('Before injury', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        # 'how_do_injury': fields.text('How do injury', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        # 'next_injury': fields.text('Next injury', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'is_lti': fields.boolean('Is LTI', readonly=True),
        # 'accident_line': fields.one2many('hse.injury.accident.line', 'injury_id', 'Accident line', readonly=True, states={'draft':[('readonly',False)]}),
        # 'corrective_action_line': fields.one2many('hse.injury.corrective.action.line', 'injury_id', 'Corrective action line', readonly=False, states={'cor_act_closed':[('readonly',True)]}),
        # 'audit_line': fields.one2many('hse.injury.audit.line', 'injury_id', 'Audit line', readonly=True, states={'draft':[('readonly',False)]}),
        # 'audit_conclusion_line': fields.one2many('hse.injury.audit.conclusion.line', 'injury_id', 'Audit conclusion line', readonly=False, states={'cor_act_closed':[('readonly',True)]}),
        # 'factor_line': fields.one2many('hse.injury.factor.line', 'injury_id', 'Factor line', readonly=True, states={'draft':[('readonly',False)]}),
        # 'attachment_ids': fields.many2many('ir.attachment', 'hse_injury_entry_ir_attachments_rel','injury_id', 'attachment_id', 'Attachments', readonly=True, states={'draft':[('readonly',False)]}),
        # 'cor_act_attach_ids': fields.many2many('ir.attachment', 'hse_injury_entry_cor_act_attach_rel','injury_id', 'attachment_id', 'Correct action image', readonly=True, states={'closed':[('readonly',False),]}),
        # 'desc_attach_ids': fields.many2many('ir.attachment', 'hse_injury_entry_desc_attach_rel','injury_id', 'attachment_id', 'Description image', readonly=True, states={'draft':[('readonly',False),]}),
        # 'mail_line': fields.one2many('hse.injury.entry.mail.line', 'injury_id', 'Mail line'),
        # 'mail_text': fields.text('Mail text'),
        'accident_cause_id': fields.many2one('hse.accident.cause','Accident cause', readonly=True),
        'factor_id': fields.many2one('hse.accident.factor', 'Factor', readonly=True),
    }
    _order = 'name asc'
    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_hse_injury_entry')
        cr.execute("""
            CREATE or REPLACE view report_hse_injury_entry as
            select 
            COALESCE(hial.id, hie.id*-1) as id,
            hie.datetime,
            hie.consequence_id,
            hie.likelihood_id,
            hie.is_lti,
            hie.department_id,
            hie.project_manager_id,
            hie.dep_manager_id,
            hie.general_master_id,
            hie.master_id,
            hie.accident_name,
            hie.lost_day,
            hie.project_id,
            hie.accident_type,
            hie.name,
            hie.location_accident,
            hial.accident_cause_id,
            hial.factor_id
            from hse_injury_entry hie
            left join hse_injury_accident_line hial on (hie.id=hial.injury_id)
            where hial.check='t'
        """)
