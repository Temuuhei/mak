#!/usr/bin/python
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
import datetime
from datetime import timedelta

_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class mak_sent_document(osv.osv):
    _name = 'mak.sent.document'

    def _set_department(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', user.id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids)[0]
            return employee.department_id.id
        else:
            raise osv.except_osv(_('Warning!'), _('You don\'t have related employee. Please contact administrator.'))
            return None

    _columns = {
        'sequence_id': fields.char('Sent Document Sequence', size=32, required=True),
        'num_sent_doc':fields.char('Index'),
        'doc_name':fields.char('About'),
        'date_doc':fields.date('Date',required=True),
        'employee_id': fields.many2one('hr.employee', 'Assigned employee'),
        'sector_id': fields.many2one('hr.department', 'Sector', domain=[('type', '=', 'sector')]),
        'director_id': fields.many2one('hr.employee', 'Assigned Director'),
        'partner_id': fields.many2one('res.partner', 'Partner'),

    }
    _defaults = {
        'date_doc': fields.datetime.now,
        'sequence_id': '/',
        'department_id': _set_department,
    }

    _order = 'sequence_id desc'

    def create(self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.sent.document')

        reg = super(mak_sent_document, self).create(cr, uid, vals, context=context)

        return reg


class mak_document_state_history(osv.osv):
    _name = 'mak.document.state.history'


    _columns = {
        'document_id': fields.many2one('mak.document', 'Mak Document'),
        'user_id':fields.many2one('res.users', 'User'),
        'date':fields.datetime('Date'),
        'old_state':fields.char('Old state'),
        'new_state':fields.char(' New State'),
        'duration':fields.float('Duration of Day')
    }



class mak_document(osv.osv):
    _name = 'mak.document'
    _descriptions = " MAK Documents"
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('wait', 'Waiting for command'),
        ('send_coworker', 'Send Coworker'),
        ('check', 'Check'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
        ('send_pomak', 'Sent PoMAK'),
    ]

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        args = args or []
        if name:
            ids = self.search(cr, uid, [('doc_name', operator, name)] + args, limit=limit, context=context or {})
            if not ids:
                ids = self.search(cr, uid, [('employee_id', operator, name)] + args, limit=limit, context=context or {})
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context or {})
        return self.name_get(cr, uid, ids, context or {})

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=None):
            res.append((doc.id, u'[%s] [%s] [%s] [%s]' % (
            doc.sequence_id, doc.num_received_document, doc.user_id.name, doc.doc_name)))
        return res

    # Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.datetime.strptime(obj.date, '%Y-%m-%d')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def _set_department(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', user.id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids)[0]
            return employee.department_id.id
        else:
            raise osv.except_osv(_('Warning!'), _('You don\'t have related employee. Please contact administrator.'))
            return None

    _columns = {
        'user_id': fields.many2one('res.users', 'Username', required=True, readonly=True),
        'sequence_id': fields.char('Regulation Sequence', size=32, required=True),
        'num_received_document': fields.char('Number of Received Documents', required=True,
                                             states={'done': [('readonly', True)]}),
        'date': fields.date('Regulation Date', required=True, states={'done': [('readonly', True)]}),
        'received_date': fields.date('Received date', required=True, states={'done': [('readonly', True)]}),
        'sector_id': fields.many2one('hr.department', 'Sector', domain=[('type', '=', 'sector')],
                                     states={'done': [('readonly', True)]}, invisible=True),
        'doc_name': fields.text('Name', size=160, required=True, states={'done': [('readonly', True)]}),
        'description': fields.text('Description', size=160, states={'done': [('readonly', True)],'send_coworker': [('required', True)]},track_visibility='onchange'),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'memo': fields.html('Content', track_visibility='onchange', states={'done': [('readonly', True)]}),
        'department_id': fields.many2one('hr.department', 'Department of employee', required=True, readonly=True),
        'date_deadline': fields.date('Deadline', states={'done': [('readonly', True)]},required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', invisible=True),
        'is_pomak': fields.boolean('Is Pomak'),
        'priority': fields.selection([('c', 'Low'), ('b', 'Medium'), ('a', 'High')], 'Priority',
                                     track_visibility='onchange', required = True),
        'send_coworker': fields.many2many('res.users', 'send_coworker_rel', 'regilation_id',
                                          'user_id', string='Send Coworkers',
                                          help="Албан тушаалтанд илгээх боломжтой ба энэ тохиолдолд заавал үр дүн талбарыг бичих ёстой."),
        'history_ids':fields.one2many('mak.document.state.history', 'document_id', 'History Documents',
                                                      readonly=True),
        'sent_doc_id':fields.many2one('mak.sent.document', 'Sent Document', readonly=True, states={'done': [('readonly', False)]})
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'received_date': fields.datetime.now,
        'date': fields.datetime.now,
        'sequence_id': '/',
        'state': 'draft',
        'department_id': _set_department,
        'priority':'c'
    }

    _order = 'date desc,priority asc'


    def create(self, cr, uid, vals, context=None):

        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.document')

        reg = super(mak_document, self).create(cr, uid, vals, context=context)

        return reg

    def unlink(self, cr, uid, ids, context=None):
        regulation = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in regulation:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
                super(mak_document, self).unlink(cr, uid, unlink_ids, context=context)
            else:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('In order to delete a regulation, you must Draft it first.'))

   # by Тэмүүжин Бусад албан тушаалтанд илгээх

    def action_send_coworker(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

        if not obj.send_coworker:
            raise osv.except_osv(_('Warning!'),
                                 _(u'Хүлээн авах хүн олдсонгүй! Та Хариуцах Албан Тушаалтан талбарыг бүртгэнэ үү!'))
        self.send_notification(cr, uid, ids, 'send_coworker', context=context)

        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'send_coworker'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        return True

    # by Тэмүүжин Шийдвэр авах
    def action_approve(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.send_notification(cr, uid, ids, 'wait', context=context)
        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'wait'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        self.write(cr, uid, ids, {'state': 'wait'})
        return True

    # by Тэмүүжин Батлах
    def action_send_pomak(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.send_notification(cr, uid, ids, 'send_pomak', context=context)
        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'send_pomak'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        return True

      # by Тэмүүжин Батлах
    def action_check(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.send_notification(cr, uid, ids, 'check', context=context)
        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'check'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        return True

    # by Тэмүүжин Батлах
    def action_done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.send_notification(cr, uid, ids, 'done', context=context)
        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'done'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        return True

    # by Тэмүүжин Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        document_history_obj = self.pool.get('mak.document.state.history')
        from_dt = datetime.datetime.strptime(obj.create_date, DATETIME_FORMAT)
        to_dt = datetime.datetime.now()
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        new_history = document_history_obj.create(cr, uid, {
            'document_id': obj.id,
            'date': datetime.datetime.now(),
            'user_id': uid,
            'old_state': obj.state,
            'duration': diff_day,
        })
        self.write(cr, uid, ids, {'state': 'draft'})
        document_history_obj.write(cr, uid, new_history, {'new_state': obj.state})
        return True


    def send_notification(self, cr, uid, ids, signal, context=None):

        for reg in self.browse(cr, SUPERUSER_ID, ids):
            model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
            groups = {

                'wait': 'group_director_of_hr',
                'send_coworker': 'base.group_user',
                'check': 'base.group_user',
                'done': 'base.group_user',
                'send_pomak': 'base.group_user',

            }
            states = {
                'wait': u'Шийд хүлээсэн',
                'send_coworker': u'"Хариуцах албан тушаалтанд илгээгдсэн" төлөвт шилжсэн',
                'check': u'"Захиргааны ажилтанд илгээгдсэн" төлөвт шилжсэн',
                'done': u'"Дууссан" төлөвт шилжсэн',
                'send_pomak': u'"Ерөнхийлөгчид илгээгдсэн" төлөвт шилжсэн',
            }

            group_user_ids = []
            notif_groups = []
            sel_user_ids = []
            # if reg.state == 'draft':
            #     notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
            #                                                   'regulation_user')
            #     template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
            #                                                                       'mak_hr_email_template_to_assigned')[
            #         1]
            # else:
            if signal in ['wait']:
                notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                              'regulation_user')
                template_id = \
                    self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                        'doc_email_template_to_hr_director')[1]
            elif signal in ['send_coworker','done']:
                template_id = \
                    self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                        'doc_email_template_to_assigned_at')[1]
                send_worker = [user.id for user in reg.send_coworker]
                group_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                                   [('id', 'in', send_worker)])

            elif signal in ['check']:
                notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                              'regulation_user')
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                  'doc_email_template_to_gov_user')[1]
            elif signal in ['send_pomak']:
                notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                              'regulation_president')
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                      'doc_email_template_to_pomak')[1]

            if notif_groups:
                sel_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                                 [('groups_id', 'in', [notif_groups[1]])])
            domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "mail.catchall.domain", context=None)
            priority = ''
            if reg.priority == 'c':
                priority = u'Энгийн'
            elif reg.priority == 'b':
                priority = u'Яаралтай'
            elif reg.priority == 'a':
                priority = u'Нэн яаралтай'

            data = {
                'doc_name': reg.doc_name,
                'department': reg.department_id.name,
                'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                'action_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                 'action_mak_document_window')[1],
                'sequence_id': reg.sequence_id,
                'id': reg.id,
                'db_name': request.session.db,
                'state': states[signal],
                'date_deadline': reg.date_deadline,
                'result': reg.description,
                'date': reg.date,
                'priority': priority,
                'num_received_document': reg.num_received_document,
                'employee_id': reg.user_id.name,
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

                self.pool.get('mak.document').message_post(cr, uid, ids, body=email, context=None)
            else:
                raise osv.except_osv(_('Warning!'), _(u'Хүлээн авах хүн олдсонгүй! Та хариуцагчийг бүртгэнэ үү!'))
            return True