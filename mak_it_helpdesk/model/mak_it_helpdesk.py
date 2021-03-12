# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbat@mak.mn
#    Phone : 976 + 99008457
#
##############################################################################

from openerp.osv import osv, fields
from datetime import date
from datetime import datetime

class mak_it_helpdesk(osv.Model):
    _name = 'mak.it.helpdesk'
    _descriptions = "MAK IT Helpdesk"
    _inherit = 'mail.thread'

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ]

    NAME_SELECTION = [
        ('program', 'Program'),
        ('internet', 'Internet'),
        ('computer', 'Computer'),
        ('printer', 'Printer/Scanner'),
        ('network', 'Network'),
        ('spark', 'Spark'),
        ('erp', 'ERP'),
        ('email', 'Email'),
        ('petram', 'Petram')
    ]

    TYPE_SELECTION = [
        ('install', 'Install Program'),
        ('error', 'Error correction'),
        ('right', 'Get right'),
        ('fix', 'Fix the problem')
    ]

    PRIORITY_SELECTION = [
        ('c', 'Low'),
        ('b', 'Medium'),
        ('a', 'High')
    ]

    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.create_date, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    _columns = {
        'sequence_id': fields.char('Sequence', size=16, required=True),
        'employee_id': fields.many2one('hr.employee', string='Employee', track_visiblity='onchange',required=True),
        'department_id': fields.many2one('hr.department', string='Department', track_visiblity='onchange',readonly=True),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'priority': fields.selection(PRIORITY_SELECTION, 'Priority', track_visibility='onchange', required=True),
        'state': fields.selection(STATE_SELECTION, 'State', track_visibility='onchange', readonly=True),
        'name': fields.selection(NAME_SELECTION, 'Name', track_visibility='onchange', required=True),
        'type': fields.selection(TYPE_SELECTION, 'Type', track_visibility='onchange', required=True),
        'assigned': fields.many2one('res.users', 'Assigned', readonly=True),
        'description': fields.text('Description', size=160,states={'done': [('readonly', True)]}),
        'done_description': fields.char('Done description', size=50, states={'done': [('readonly', True)]}),
    }

    def _employee_get(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', user.id)])
        if employee_ids[0]:
            return employee_ids[0]
        else:
            return None

    def _department_get(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', user.id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids)[0]
            return employee.department_id.id
        else:
            return None

    _defaults = {
        'employee_id': _employee_get,
        'department_id': _department_get,
        'sequence_id': '/',
        'name': 'computer',
        'type': 'error',
        'state': 'draft',
        'priority': 'b'
    }

    _order = "create_date desc"

    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.it.helpdesk')
        reg = super(mak_it_helpdesk, self).create(cr, uid, vals, context=context)
        return reg

    def action_sent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'sent'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        self.write(cr, uid, ids, {'assigned': uid})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.write(cr, uid, ids, {'assigned': uid})
        return True