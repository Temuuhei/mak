# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbat.k@mak.mn
#    Phone : 99008457
#
##############################################################################

from openerp.osv import osv, fields
from datetime import datetime
from datetime import date

class mak_security(osv.Model):
    _name = 'mak.security'
    _descriptions = "MAK security report"
    _inherit = 'mail.thread'
    _order = "date desc"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent')
    ]

    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.date, '%Y-%m-%d')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    _columns = {
        'department_id': fields.many2one('hr.department', string='Sector'),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'date': fields.date('Date', default = date.today(), states={'sent': [('readonly', True)]}),
        'breach': fields.selection([('yes', 'Yes'),('no', 'No')], 'Breach', track_visibility='onchange', states={'sent': [('readonly', True)]}),
        'description': fields.text('Description', size=400, states={'sent': [('readonly', True)]}),
        'state': fields.selection(STATE_SELECTION, 'State', track_visibility='onchange')
    }

    def get_sector(self, cr, uid, dep_id):
        dep_obj = self.pool.get('hr.department')
        department = dep_obj.browse(cr, uid, [dep_id])[0]
        if department.type == 'sector' or department.type == 'project':
            return department.id
        elif department['parent_id'].type == 'sector' or department.type == 'project':
            return department['parent_id'].id
        elif not department['parent_id']:
            return department.id
        else:
            return self.get_sector(cr, uid, department['parent_id'].id)

    def _department_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            dep_id = self.pool.get('hr.employee').browse(cr, uid, ids[0])['department_id'].id
            dep_id2 = self.get_sector(cr, uid, dep_id)
            return dep_id2
        return False

    _defaults = {
        'state': 'draft',
        'department_id': _department_get,
    }

    def action_sent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'sent'})
        return True