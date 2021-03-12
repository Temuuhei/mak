# -*- coding: utf-8 -*-
##############################################################################
#
# Mongolyn Alt LLC, Enterprise Management Solution
# Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn/, http://asterisk-tech.mn/&gt;). All Rights Reserved #
# Email : temuujintsogt@gmail.com
# Phone : 976 + 99741074
#
##############################################################################
import time
import math
import openerp.pooler
import openerp.tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.netsvc
import sys
import logging
from openerp.addons.crm import crm
from datetime import timedelta
from datetime import datetime
from datetime import date
from dateutil import parser
from openerp import SUPERUSER_ID
from openerp.http import request
from lxml import etree

_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class task_management(osv.osv):
    _name = 'task.management'
    _descriptions = " MAK Task Management"
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('assigned', 'Assigned'),
        ('check', 'Check'),
        ('to_partner', 'To partner'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ]

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        if name:
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context or {})
            if not ids:
                ids = self.search(cr, uid, [('employee_id', operator, name)] + args, limit=limit, context=context or {})
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context or {})
        return self.name_get(cr, uid, ids, context or {})

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for task in self.browse(cr, uid, ids, context=None):
            res.append((task.id, u'[%s] [%s] [%s]' % (
                task.sequence_id, task.sector_id.name, task.name)))
        return res

    # Өдөрөөр салгах
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
        'assigned_id': fields.many2many('res.users', 'notify_task_assigners_rel', 'task_management_id',
                                               'user_id', string='Assigned To',track_visibility='onchange'),
        'sequence_id': fields.char('Task Sequence', size=32, required=True),
        'date': fields.date('Date', required=True, states={'done': [('readonly', True)]}),
        'assigned_date': fields.date('Assigned Date'),
        'check_date': fields.date('Checked Date'),
        'sector_id': fields.many2one('hr.department', 'Sector', domain=[('type', '=', 'sector')],
                                     states={'done': [('readonly', True)]}, invisible=True),
        'partner_id': fields.many2one('res.partner', 'Partner', states={'done': [('readonly', True)]}),
        'type': fields.selection([('contract', 'Contract'), ('other', 'Other')], 'Type',
                                 states={'done': [('readonly', True)]}),
        'name': fields.text('Name', size=160, required=True, states={'done': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'memo': fields.html('Content', track_visibility='onchange', states={'done': [('readonly', True)]}),
        'date_deadline': fields.date('Deadline', required=True, states={'done': [('readonly', True)],'assigned': [('readonly', True)],'check': [('readonly', True)]}),
        'priority': fields.selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], 'Priority',
                                     track_visibility='onchange'),
        'duration':fields.float('Duration'),
        'is_expired':fields.boolean('Is expired?')
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'date': fields.datetime.now,
        'sequence_id': '/',
        'state': 'draft',
        'is_expired': False,
    }

    _order = 'date desc,assigned_id asc'

    def create(self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'task.management')
        reg = super(task_management, self).create(cr, uid, vals, context=context)
        return reg

    def unlink(self, cr, uid, ids, context=None):
        regulation = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in regulation:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
                super(task_management, self).unlink(cr, uid, unlink_ids, context=context)
            else:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('In order to delete a task, you must Draft it first.'))

    def action_assigned(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if obj.state == 'draft':
            if not obj.assigned_id:
                raise osv.except_osv(_('Invalid Action!'),
                               _('you must choose assigner it first.'))
            self.write(cr, uid, ids, {'state': 'assigned',
                                      'assigned_date': fields.datetime.now(date)})
            self.send_notification(cr, uid, ids, 'assigned', context=context)
        return True

    def action_check(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        duration = 0.0
        if obj.state == 'assigned':
            self.write(cr, uid, ids, {'state': 'check',
                                      'check_date': fields.datetime.now(date)})
        if obj.assigned_date and obj.check_date:
            d1 = datetime.strptime(obj.assigned_date, "%Y-%m-%d")
            d2 = datetime.strptime(obj.check_date, "%Y-%m-%d")
            d23 = datetime.strptime(obj.date_deadline, "%Y-%m-%d")
            duration = (d2 - d1).days
            print 'duration \n',duration
            duration += duration
            self.write(cr, uid, ids, {'duration': duration})
            if d2 > d23:
                self.write(cr, uid, ids, {'is_expired': True})
            self.send_notification(cr, uid, ids, 'check', context=context)
            self.write(cr, uid, ids, {'state': 'check'})
        return True

    # by Тэмүүжин Дуусгах
    def action_done(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'done', context=context)
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    # by Тэмүүжин цуцлах
    def action_cancel(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'cancel', context=context)
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    # by Тэмүүжин харилцагчид илгээгдсэн
    def action_to_partner(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'to_partner', context=context)
        self.write(cr, uid, ids, {'state': 'to_partner'})
        return True

        # by Тэмүүжин томилогдсон
    def action_back(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'assigned', context=context)
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True

    # by Тэмүүжин Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def send_notification(self, cr, uid, ids, signal, context=None):

        for task in self.browse(cr, SUPERUSER_ID, ids):
            model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
            groups = {

                'assigned': 'base.group_user',
                'check': 'base.group_user',
                'done': 'base.group_user',
                'cancel': 'base.group_user',
            }
            states = {
                'assigned': u'"Ноорог" → "Хуульч томилогдсон" төлөвт шилжсэн',
                'check': u'"Хуульч томилогдсон" → "Шалгах" төлөвт шилжсэн',
                'done': u'"Шалгах" → "Дууссан" төлөвт шилжсэн',
                'cancel': u'Цуцлагдсан',
            }

            group_user_ids = []
            notif_groups = []
            sel_user_ids = []
            if signal in ['assigned', 'done','cancel']:
                template_id = \
                    self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_work_task',
                                                                        'task_management_email_template_to_user')[1]
                group_user_ids = [user.id for user in task.assigned_id]
            elif signal in ['check']:
                notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_work_task',
                                                              'task_management_manager')
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_work_task',
                                                                                  'task_email_template_to_manager')[1]

        if notif_groups or group_user_ids:
            print 'notif_groups \n',notif_groups,type(notif_groups)
            if notif_groups:
                sel_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                             [('groups_id', 'in', notif_groups[1])])

            domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "mail.catchall.domain", context=None)

            data = {
                'name': task.name,
                'department': task.sector_id.name,
                'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                'action_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_work_task',
                                                                                 'action_task_management_window')[1],
                'sequence_id': task.sequence_id,
                'id': task.id,
                'db_name': request.session.db,
                'state': states[signal],
                'date_deadline': task.date_deadline,
                'type': task.type,
                'date': task.date,
                'duration': task.duration,
                'assigned_id': task.assigned_id[0].name,
                'sender': self.pool.get('res.users').browse(cr, uid, uid).name,
            }
            if not group_user_ids:
                group_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID, [('id', 'in', sel_user_ids)])
            if group_user_ids:
                # group_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID, [('id', 'in', sel_user_ids)])
                users = self.pool.get('res.users').browse(cr, uid, group_user_ids)
                user_emails = []
                for user in users:
                    user_emails.append(user.login)
                    self.pool.get('email.template').send_mail(cr, uid, template_id, user.id, force_send=True,
                                                              context=data)
                email = u'' + states[signal] + u'.\n Дараах хэрэглэгч рүү имэйл илгээгдэв : ' + (
                    '<b>' + ('</b>, <b>'.join(user_emails)) + '</b>')

                self.pool.get('task.management').message_post(cr, uid, ids, body=email, context=None)
            else:
                raise osv.except_osv(_('Warning!'), _(u'Хүлээн авах хүн олдсонгүй! Та хариуцагчийг бүртгэнэ үү!'))
            return True