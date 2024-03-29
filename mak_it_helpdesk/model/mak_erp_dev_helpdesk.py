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
from openerp import api
from openerp.tools.translate import _


class mak_erp_dev_helpdesk(osv.Model):
    _name = 'mak.erp.dev.helpdesk'
    _descriptions = "MAK ERP development Helpdesk"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = "create_date desc"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approve', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('moved', 'Moved')
    ]

    TYPE_SELECTION = [
        ('error', u'Алдаа'),
        ('imp', u'Сайжруулалт'),
        ('delete', u'Мэдээлэл устгах'),
        ('change', u'Мэдээлэл өөрчилөх'),
        ('new_report', u'Шинэ тайлан'),
    ]

    DONE_TYPE_SELECTION = [
        ('user', u'Хэрэглэгчийн гаргасан алдаа'),
        ('acl', u'Эрхийн тохиргооноос болсон'),
        ('config', u'Тохиргоо буруу хийгдсэн'),
        ('requirement', u'Хэрэглэгчийн шаардлага дутуу байсан'),
        ('development', u'Хөгжүүлэлтийн алдаа'),
        ('oderp_solution', u'OdErp шийдлээс хамаарсан'),
        ('core_solution', u'Core шийдлээс хамаарсан'),
    ]

    PRIORITY_SELECTION = [
        ('r', 'Regular'),
        ('m', 'Medium'),
        ('h', 'High')
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
        'type': fields.selection(TYPE_SELECTION, 'Type', track_visibility='onchange', required=True, default='error'),

        'purpose': fields.text('Purpose', states={'done': [('readonly', True)]}),
        'problem': fields.text('Problem', states={'done': [('readonly', True)]}),
        'result': fields.text('Result', states={'done': [('readonly', True)]}),

        'menu_sequence': fields.text('Menu sequence', states={'done': [('readonly', True)]}),
        'window_name': fields.text('Window name', states={'done': [('readonly', True)]}),
        'done_action': fields.text('Done action', states={'done': [('readonly', True)]}),

        'description': fields.text('Description', size=160, states={'done': [('readonly', True)]}),
        'state': fields.selection(STATE_SELECTION, 'State', track_visibility='onchange', readonly=True),
        'dir': fields.many2one('res.users', 'Director', readonly=True),
        'assigned': fields.many2one('res.users', 'Assigned', readonly=True),
        'done_description': fields.text('Done description', size=150, states={'done': [('readonly', True)]}),
        'done_type': fields.selection(DONE_TYPE_SELECTION, 'Done type', track_visibility='onchange'),
    }

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=None):
            res.append((doc.id, u'[%s] [%s] [%s]' % (doc.employee_id.name, doc.type, doc.create_date)))
        return res

    def unlink(self, cr, uid, ids, context=None):
        regulation = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in regulation:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
                super(mak_erp_dev_helpdesk, self).unlink(cr, uid, unlink_ids, context=context)
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
        'priority': 'r'
    }

    def create(self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.erp.dev.helpdesk')
        reg = super(mak_erp_dev_helpdesk, self).create(cr, uid, vals, context=context)
        return reg

    def action_sent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if obj.type == "error":
            obj.write({'state': 'approve'})
        else:
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

    def action_move_it(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        new_mak_it_helpdesk_create_dict = {
            "priority": "b",
            "job": "erp",
            "type": "right",
        }
        if obj.department_id:
            new_mak_it_helpdesk_create_dict.update(
                {"department_id": obj.department_id.id}
            )
        if obj.employee_id:
            new_mak_it_helpdesk_create_dict.update(
                {"employee_id": obj.employee_id.id}
            )
        if obj.year:
            new_mak_it_helpdesk_create_dict.update(
                {"year": obj.year}
            )
        if obj.month:
            new_mak_it_helpdesk_create_dict.update(
                {"month": obj.month}
            )
        if obj.day:
            new_mak_it_helpdesk_create_dict.update(
                {"day": obj.day}
            )
        if obj.description:
            new_mak_it_helpdesk_create_dict.update(
                {"description": obj.description}
            )
        if obj.state:
            new_mak_it_helpdesk_create_dict.update(
                {"state": obj.state}
            )
        if obj.dir:
            new_mak_it_helpdesk_create_dict.update(
                {"dir": obj.dir.id}
            )

        # new_mak_it_helpdesk_create_obj = self.env['mak.it.helpdesk'].create(new_mak_it_helpdesk_create_dict)
        new_mak_it_helpdesk_create_obj = self.pool.get('mak.it.helpdesk').create(cr, uid, new_mak_it_helpdesk_create_dict, context=context)

        obj.write({
            'state': 'cancel',
            'assigned': uid
        })
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        self.write(cr, uid, ids, {'assigned': uid})
        return True

    def action_migrate(self, cr, uid, ids, context=None):
        if not ids: return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_it_helpdesk', 'migrate_to_it_helpdesk_form')

        current_helpdesk = self.browse(cr, uid, ids[0], context=context)

        context = dict(context or {})
        context.update({
            'default_dev_helpdesk': current_helpdesk.id
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
            'name':_("Migrate to IT Helpdesk"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'migrate.to.it.helpdesk',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context
        }
