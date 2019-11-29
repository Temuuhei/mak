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
_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class  mak_reminder(osv.Model):
    _name = 'mak.reminder'
    _descriptions = " MAK Reminders"
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Done')
    ]
    # Өдөрөөр салгах
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
        'user_id': fields.many2one('res.users', 'Username', required=True, readonly=True),
        'assigned_id': fields.many2many('res.users', 'notify_reminder_assigners_rel', 'reminder_id',
                                               'user_id', string='Assigned To',track_visibility='onchange'),
        'sequence_id': fields.char('Reminder Sequence', size=32, required=True),
        'description': fields.text('Description', size=160, states={'done': [('readonly', True)]}),
        'notify_day': fields.integer('Notify Day', states={'done': [('readonly', True)]},track_visibility='onchange'),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'date_deadline': fields.date('Deadline', states={'done': [('readonly', True)]}),
        'priority': fields.selection([('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], 'Priority',
                                     track_visibility='onchange'),
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'sequence_id': '/',
        'state': 'draft',
    }

    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.reminder')
        reg = super(mak_reminder, self).create(cr, uid, vals, context=context)
        return reg

    # by Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    # by Тэмүүжин Батлах
    def action_done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def _send_reminder_notification(self, cr, uid, context=None):
        print '_send_reminder_notification....'
        context = context or {}
        user_ids = []
        reminder_obj = self.pool.get('mak.reminder')
        land_ids = self.pool.get('mak.reminder').search(cr, uid,
                                                       [('state', '=', 'done')])
        model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
        current_date = time.strftime('%Y-%m-%d')
        # current_date = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=45)
        contract_manager_group = model_obj.get_object_reference(cr, uid, 'l10n_mn_contract_management',
                                                                'group_contract_manager')
        template_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_reminder',
                                                            'mak_reminder_send_alarm')[1]
        if land_ids:
            reminders = reminder_obj.browse(cr,uid,land_ids)
            for l in reminders:
                if l.assigned_id and l.notify_day > 0:
                    current_date = datetime.strptime(current_date, '%Y-%m-%d') + timedelta(days=int(l.notify_day))
                    if datetime.strptime(l.date_deadline, '%Y-%m-%d') <= current_date:
                        data = {
                            'name': l.description,
                            'notify_day': l.notify_day,
                            'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                            'action_id':
                                self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_reminder',
                                                                                    'action_mak_reminder_window')[1],
                            'id': l.id,
                            'db_name': cr.dbname,
                        }
                        user_ids = []
                        if l.assigned_id:
                            for a in l.assigned_id:
                                if a.id not in user_ids:
                                    user_ids.append(a.id)
                        if user_ids:
                            users = self.pool.get('res.users').browse(cr, uid, user_ids)
                            user_emails = []
                            for user in users:
                                user_emails.append(user.login)
                                self.pool.get('email.template').send_mail(cr, uid, template_id, user.id, force_send=True,
                                                                          context=data)
                                user_ids.append(user.id)
                            email = u'' + u'.\n Дараах хэрэглэгчид рүү имэйл илгээгдэв: ' + (
                            '<b>' + ('</b>, <b>'.join(user_emails)) + '</b>')
                            self.pool.get('mak.reminder').message_post(cr, uid, l.id, body=email, context=None)
                        else:
                            raise ValidationError(
                                _('Имэйл хаяггүй хэрэглэгч байгаа тул илгээж чадсангүй. Админтай холбогдоно уу.'))


