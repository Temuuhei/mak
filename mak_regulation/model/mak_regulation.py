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


class hr_regulation(osv.osv):
    _inherit = "hr.regulation"

    _columns = {

        'origin': fields.many2one('mak.regulation', 'Origin document',
                                              states={'confirmed': [('readonly', True)]}),

    }



class mak_regulation(osv.osv):
    _name = 'mak.regulation'
    _descriptions = " MAK HR Regulations"
    _inherit = ['mail.thread']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('wait', 'Waiting for command'),
        ('assigned', 'Assigned'),
        ('open1', 'Open(I)'),
        ('pending1', 'Pending(I)'),
        ('assigned2', 'Assigned (II)'),
        ('open2', 'Open(II)'),
        ('pending2', 'Penging(II)'),
        ('check', 'Check'),
        ('done', 'Done'),
        ('send_pomak', 'Sent to PoMAK'),
        ('to_allow', 'Allow of PoMAK'),
        ('to_reject', 'Reject of PoMAK'),
        ('created_reg', 'Created Regulation'),
        ('cancel', 'Cancel'),
         ]


    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=context):
            res.append( (doc.id, u'[%s] [%s] [%s] [%s]' % (doc.sequence_id,doc.num_received_document, doc.employee_id.name,doc.doc_name)))
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

    def _set_department(self, cr, uid, ids, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid)
        employee_ids = self.pool.get('hr.employee').search(cr, uid,[('user_id','=',user.id)])
        if employee_ids:
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_ids)[0]
            return employee.department_id.id
        else:
            raise osv.except_osv(_('Warning!'), _('You don\'t have related employee. Please contact administrator.'))
            return None

    _columns = {
        'user_id': fields.many2one('res.users', 'Employee', required=True, readonly=True),
        'assigned_id': fields.many2one('res.users', 'Assigned To',states={'done': [('readonly', True)]}),
        'assigned_id2': fields.many2one('res.users', '2nd Assigned To',states={'done': [('readonly', True)]}),
        'sequence_id': fields.char('Regulation Sequence', size=32, required=True),
        'num_received_document': fields.char('Number of Received Documents', required=True,states={'done': [('readonly', True)]}),
        'date': fields.date('Regulation Date', required=True,states={'done': [('readonly', True)]}),
        'received_date': fields.date('Received date', required=True,states={'done': [('readonly', True)]}),
        'sector_id': fields.many2one('hr.department', 'Sector', domain=[('type', '=', 'sector')],states={'done': [('readonly', True)]},invisible = True),
        'type': fields.selection([('local', 'Local'), ('abroad', 'Abroad')],'Type',states={'done': [('readonly', True)]}),
        'type_doc': fields.selection([('official_doc', 'Official Document'), ('complain', 'Complain')],'Document Type',states={'done': [('readonly', True)]}),
        'doc_name': fields.text('Name', size=160, required=True,states={'done': [('readonly', True)]}),
        'description': fields.text('Description', size=160,states={'done': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'memo': fields.html('Content',track_visibility='onchange',states={'done': [('readonly', True)]}),
        'department_id': fields.many2one('hr.department', 'Department of employee', required=True, readonly=True),
        'reg_attachment_id': fields.many2many('ir.attachment', 'regulation_ir_attachments_rel', 'reg_id', 'attachment_id',
                                               'Attachment',track_visibility='onchange'),
        'reg_attachment_director_id': fields.binary('Attachment of Director',track_visibility='onchange'),
        'date_deadline': fields.date('Deadline',states={'done': [('readonly', True)]}),
        'partner_id' : fields.many2one('res.partner', 'Partner', invisible = True),
        'partner' : fields.char('Partner', invisible = True),
        'employee_id' : fields.many2one ('hr.employee', 'Employee',invisible = True),
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'received_date': fields.datetime.now,
        'date': fields.datetime.now,
        'sequence_id': '/',
        'state': 'draft',
        'department_id': _set_department,
    }

    _order = 'date desc'

    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.regulation')
        reg = super(mak_regulation, self).create(cr, uid, vals, context=context)
        return reg

    def unlink(self, cr, uid, ids, context=None):
        regulation = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in regulation:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
                super(mak_regulation, self).unlink(cr, uid, unlink_ids, context=context)
            else:
                raise osv.except_osv(_('Invalid Action!'),
                                     _('In order to delete a regulation, you must Draft it first.'))

    def action_second_stage(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if obj.state == 'pending1':
            self.send_notification(cr, uid, ids, 'assigned2', context=context)
            self.write(cr, uid, ids, {'state': 'assigned2'})
        return True

    def action_next(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if obj.state == 'wait':
            self.send_notification(cr, uid, ids, 'assigned', context=context)
            self.write(cr, uid, ids, {'state': 'assigned'})
        elif obj.state == 'assigned':
            self.write(cr, uid, ids, {'state': 'open1'})
        elif obj.state == 'open1':
            self.write(cr, uid, ids, {'state': 'pending1'})
        elif obj.state == 'assigned2':
            self.write(cr, uid, ids, {'state': 'open2'})
        elif obj.state == 'open2':
            self.write(cr, uid, ids, {'state': 'pending2'})
        return True

    def action_previous(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        if obj.state == 'assigned':
            self.write(cr, uid, ids, {'state': 'wait'})
        if obj.state == 'open1':
            self.write(cr, uid, ids, {'state': 'assigned'})
        if obj.state == 'pending1':
            self.write(cr, uid, ids, {'state': 'open1'})
        if obj.state == 'assigned2':
            self.write(cr, uid, ids, {'state': 'pending1'})
        if obj.state == 'open2':
            self.write(cr, uid, ids, {'state': 'assigned2'})
        if obj.state == 'pending2':
            self.write(cr, uid, ids, {'state': 'open2'})
        if obj.state == 'check':
            self.write(cr, uid, ids, {'state': 'pending2'})
        return True

    # by Тэмүүжин Батлах
    def action_approve(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'wait', context=context)
        self.write(cr, uid, ids, {'state': 'wait'})
        return True
    
    # by Тэмүүжин Батлах
    def action_send_pomak(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'send_pomak', context=context)
        self.write(cr, uid, ids, {'state': 'send_pomak'})
        return True

    # by Тэмүүжин Батлах
    def action_allow(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'to_allow', context=context)
        self.write(cr, uid, ids, {'state': 'to_allow'})
        return True

    # by Тэмүүжин Батлах
    def action_reject(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'to_reject', context=context)
        self.write(cr, uid, ids, {'state': 'to_reject'})
        return True

    def action_create_reg(self,cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)[0]
        return {
            'name': ('Regulation Registry'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.regulation',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_origin': obj.id,}
        }
        self.write(cr, uid, ids,{'state':'created_reg'})



    # by Тэмүүжин Батлах
    def action_check(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'check', context=context)
        self.write(cr, uid, ids, {'state': 'check'})
        return True

    # by Тэмүүжин Батлах
    def action_done(self, cr, uid, ids, context=None):
        self.send_notification(cr, uid, ids, 'done', context=context)
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    # by Тэмүүжин Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def send_notification(self, cr, uid, ids, signal, context=None):

        for reg in self.browse(cr, SUPERUSER_ID, ids):
            model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
            groups = {

                'wait': 'group_director_of_hr',
                'assigned': 'base.group_user',
                'assigned2': 'base.group_user',
                'check': 'base.group_user',
                'done': 'base.group_user',
                'cancel': 'base.group_user',
                'created_reg': 'base.group_user',
                'send_pomak': 'group_regulation_president',
                'to_allow': 'base.group_user',
                'to_reject': 'base.group_user',
            }
            states = {
                'wait': u'Шийд хүлээсэн',
                'assigned': u'"Шийд хүлээсэн" → "Хариуцагч томилогдсон" төлөвт шилжсэн',
                'assigned2': u'"Хийгдэж байна" → "Хариуцагчтай(II шат) томилогдсон" төлөвт шилжсэн',
                'check': u'"Хийгдэж байна or Хйигдэж байна(II)" → "БХГ-ийн захиралд илгээгдсэн" төлөвт шилжсэн',
                'done': u'"БХГ-ийн захиралд илгээгдсэн" → "Дууссан" төлөвт шилжсэн',
                'cancel': u'Цуцлагдсан',
                'created_reg': u'"Дууссан" → "Тушаал үүссэн" төлөвт шилжсэн',
                'send_pomak': u'"Дууссан" → "Ерөнхийлөгчид илгээсэн" төлөвт шилжсэн',
                'to_allow': u'"Ерөнхийлөгчид илгээсэн" → "Ерөнхийлөгч зөвшөөрсөн" төлөвт шилжсэн',
                'to_reject': u'"Ерөнхийлөгчид илгээсэн" → "Ерөнхийлөгч татгалзсан" төлөвт шилжсэн',
            }

            group_user_ids = []
            notif_groups = []
            sel_user_ids = []
            if reg.state == 'draft':
                notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                              'regulation_user')
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                  'mak_hr_email_template_to_assigned')[1]
            else:
                if signal in ['assigned','done','to_allow','to_reject']:
                    # notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                    #                                               groups[signal])
                    template_id = \
                    self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                        'reg_email_template_to_user')[1]
                    group_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                                           [('id', '=', reg.assigned_id.id)])
                    # notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                    #                                               'regulation_user')
                    # print 'NOTIFF GROUPS \n\n',notif_groups,group_user_ids

                elif signal in ['assigned2','done','to_allow','to_reject']:

                    # notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                    #                                               groups[signal])
                    template_id = \
                        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                            'reg_email_template_to_user')[1]
                    group_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                                       [('id', '=', reg.assigned_id2.id)])
                elif signal in ['check','to_allow','to_reject']:
                    notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                                  'regulation_user')
                    template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                      'reg_email_template_to_user')[1]
                elif signal in ['send_pomak']:
                    notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_regulation',
                                                                  'regulation_president')
                    template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation',
                                                                                      'reg_email_template_to_pomak')[1]


            if notif_groups:
                sel_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,
                                                                 [('groups_id', 'in', [notif_groups[1]])])
            domain = self.pool.get("ir.config_parameter").get_param(cr, uid, "mail.catchall.domain", context=None)

            data = {
                'doc_name': reg.doc_name,
                'department': reg.department_id.name,
                'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                'action_id': self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_regulation','action_mak_regulation_window')[1],
                'sequence_id': reg.sequence_id,
                'id': reg.id,
                'db_name': request.session.db,
                'state': states[signal],
                'date_deadline': reg.date_deadline,
                'doc_type': reg.type_doc,
                'date': reg.date,
                'last_name': reg.employee_id.last_name,
                'department_id': reg.employee_id.department_id.name,
                'job_id': reg.employee_id.job_id.name,
                'num_received_document': reg.num_received_document,
                'employee_id': reg.employee_id.name,
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

                self.pool.get('mak.regulation').message_post(cr, uid, ids, body=email, context=None)
            else:
                raise osv.except_osv(_('Warning!'), _(u'Хүлээн авах хүн олдсонгүй! Та хариуцагчийг бүртгэнэ үү!'))
            return True