# -*- coding: utf-8 -*-
##############################################################################
#
#   MAK LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.asterisk-tech.mn>). All Rights Reserved
#
#    Email : munkhbat.k@mak.mn
#    Phone : 99008457
#    Date  : 2021/05/19
##############################################################################

from openerp.osv import osv, fields
from datetime import datetime

class hr_department(osv.osv):
    _inherit = 'hr.department'

    _columns = {
        'is_sec' : fields.boolean('Is Security', default = False)
    }
class mak_security(osv.osv):
    _name = 'mak.security'
    _descriptions = "MAK security report"
    _inherit = 'mail.thread'
    _order = "start_datetime desc"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent')
    ]

    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.start_datetime, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    _columns = {
        'department_id': fields.many2one('hr.department', string='Department',readonly=1),
        'point': fields.char('Point', states={'sent':[('readonly',True)]}),
        'employee_id': fields.many2one('hr.employee', string='Assigned To', states={'sent':[('readonly',True)]}),
        'received_employee_id': fields.many2one('hr.employee',  string='Received', track_visiblity='onchange', states={'sent':[('readonly',True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'start_datetime': fields.datetime('Start date', states={'sent':[('readonly',True)]}),
        'end_datetime': fields.datetime('End date', states={'sent':[('readonly',True)]}),
        'problem': fields.selection([('yes', 'Notnormal'), ('no', 'Normal')], 'Problem', track_visibility='onchange', states={'sent':[('readonly',True)]}),
        'note_motion': fields.text('Note motion', size=500, states={'sent':[('readonly',True)]}),
        'note_electric': fields.text('Note electric', size=200, states={'sent':[('readonly',True)]}),
        'note_car': fields.text('Note car', size=200, states={'sent':[('readonly',True)]}),
        'note_work': fields.text('Note work', size=200, states={'sent':[('readonly',True)]}),
        'note_check': fields.text('Note work', size=300, states={'sent':[('readonly',True)]}),
        'note_gate': fields.text('Note gate', size=300, states={'sent':[('readonly',True)]}),
        'note_time': fields.text('Note time', size=200, states={'sent':[('readonly',True)]}),
        'note_security': fields.text('Note security', size=300, states={'sent':[('readonly',True)]}),
        'task': fields.text('Task', size=300),
        'state': fields.selection(STATE_SELECTION, 'State', track_visibility='onchange')
    }

    def _department_get(self, cr, uid, ids, context=None):
        dep_id = self.pool.get('res.users').browse(cr, uid, uid)['department_id'].id
        return dep_id

    _defaults = {
        'state': 'draft',
        'start_datetime': datetime.now(),
        'department_id': _department_get
    }

    def action_sent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'sent'})
        return True