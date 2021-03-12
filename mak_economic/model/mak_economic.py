# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbat.k@mak.mn, bayarbold.b@mak.mn
#    Phone : 99008457, 99904330
#
##############################################################################

from openerp.osv import osv, fields
from datetime import date
from datetime import datetime

class mak_economic(osv.Model):
    _name = 'mak.economic'
    _descriptions = "MAK economic research"
    _inherit = 'mail.thread'

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
        'employee_id': fields.many2one('hr.employee', string='Assigned To', track_visiblity='onchange'),
        'department_id': fields.many2one('hr.department', string='Sector',domain = [('type', '=', 'sector')], track_visiblity='onchange'),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'date': fields.date('Date', default = date.today()),
        'name': fields.char('Name'),
        'description': fields.text('Description', size=160)
    }

    def _employee_get(self, cr, uid, context=None):
        emp_id = context.get('default_employee_id', False)
        if emp_id:
            return emp_id
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _department_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            dep_id = self.pool.get('hr.employee').browse(cr, uid, ids[0])['department_id'].id
            return dep_id
        return False


    _defaults = {
        'employee_id': _employee_get,
        'department_id': _department_get,
    }

    _order = "create_date desc"
