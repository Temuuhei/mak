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
from datetime import datetime
from openerp.tools.translate import _


class mak_it_helpdesk(osv.Model):
    _name = 'mak.it.helpdesk'
    _descriptions = "MAK IT Helpdesk"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approve', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('moved', 'Moved')
    ]

    PROGRAM_SELECTION = [
        ('program', 'Program'),
        ('internet', 'Internet'),
        ('computer', 'Computer'),
        ('printer', 'Printer/Scanner'),
        ('network', 'Network'),
        ('erp', 'ERP'),
        ('email', 'Email'),
        ('spark', 'Spark'),
        ('pitram', 'Pitram'),
    ]

    TYPE_SELECTION = [
        ('service', 'Get service'),
        ('right', 'Get program right'),
        ('pass', 'Change user password')
    ]

    PRIORITY_SELECTION = [
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
        'department_id': fields.many2one('hr.department', string='Department', track_visiblity='onchange',
                                         readonly=True),
        'employee_id': fields.many2one('hr.employee', string='Employee', track_visiblity='onchange', required=True,
                                       domain="[('department_id','=',department_id),('state_id.type', 'not in', ('resigned', 'contract', 'student', 'end_contract'))]"),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'priority': fields.selection(PRIORITY_SELECTION, 'Priority', track_visibility='onchange', required=True),
        'job': fields.selection(PROGRAM_SELECTION, 'Job', track_visibility='onchange', required=True),
        'type': fields.selection(TYPE_SELECTION, 'Type', track_visibility='onchange', required=True),
        'description': fields.text('Description', size=160, states={'done': [('readonly', True)]}),
        'state': fields.selection(STATE_SELECTION, 'State', track_visibility='onchange', readonly=True),
        'dir': fields.many2one('res.users', 'Director', readonly=True),
        'assigned': fields.many2one('res.users', 'Assigned', readonly=True),
        'done_description': fields.text('Done description', size=150, states={'done': [('readonly', True)]}),
    }

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=None):
            res.append((doc.id, u'[%s] [%s] [%s]' % (doc.employee_id.name, doc.job, doc.type)))
        return res

    def unlink(self, cr, uid, ids, context=None):
        regulation = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in regulation:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
                super(mak_it_helpdesk, self).unlink(cr, uid, unlink_ids, context=context)
            else:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('In order to delete a task, you must Draft it first.'))

    def _department_get(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', user.id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids)[0]
            return employee.department_id.id
        else:
            raise osv.except_osv(_('Warning!'), _('You don\'t have related employee. Please contact administrator.'))
            return None

    _defaults = {
        'department_id': _department_get,
        'state': 'draft',
        'priority': 'b'
    }

    _order = "create_date desc"

    def create(self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.it.helpdesk')
        reg = super(mak_it_helpdesk, self).create(cr, uid, vals, context=context)
        return reg

    def action_sent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'sent'})
        return True

    def action_return(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approve'})
        self.write(cr, uid, ids, {'dir': uid})
        return True

    def action_disapprove(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'disapprove'})
        self.write(cr, uid, ids, {'dir': uid})
        return True

    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        self.write(cr, uid, ids, {'assigned': uid})
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.write(cr, uid, ids, {'assigned': uid})
        return True

    def action_migrate(self, cr, uid, ids, context=None):
        # id = self.copy(cr, uid, ids[0], context=context)
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_it_helpdesk', 'migrate_to_dev_helpdesk_form')
        view_id = view_ref and view_ref[1] or False,

        current_helpdesk = self.browse(cr, uid, ids[0], context)

        context = dict(context or {})
        context.update({
            'default_it_helpdesk': current_helpdesk.id
        })
        if current_helpdesk.department_id:
            context.update({
                'default_department_id': current_helpdesk.department_id.id,
            })
        if current_helpdesk.employee_id:
            context.update({
                'default_employee_id': current_helpdesk.employee_id.id,
            })
        if current_helpdesk.dir:
            context.update({
                'default_dir': current_helpdesk.dir.id,
            })
        if current_helpdesk.year:
            context.update({
                'default_year': current_helpdesk.year,
            })
        if current_helpdesk.month:
            context.update({
                'default_month': current_helpdesk.month,
            })
        if current_helpdesk.day:
            context.update({
                'default_day': current_helpdesk.day,
            })
        if current_helpdesk.description:
            context.update({
                'default_description': current_helpdesk.description,
            })
        if current_helpdesk.state:
            context.update({
                'default_state': current_helpdesk.state,
            })
        return {
            'type': 'ir.actions.act_window',
            'name': _('Migrate to ERP dev Helpdesk'),
            'res_model': 'migrate.to.dev.helpdesk',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'nodestroy': True,
            'context': context,
        }
        return True
