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

class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'is_blackened': fields.boolean(string = 'Is Blackened'),
        'date_blackened': fields.date(string = 'Date blackened', track_visibility='onchange')
    }


class mak_audit(osv.osv):
    _name = 'mak.audit'
    _description = "MAK Audit department"
    _inherit = ['mail.thread']
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),]

    # Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.received_date, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    _columns = {
        'user_id': fields.many2one('res.users', 'Employee', required=True, readonly=True),
        'assigned_id': fields.many2one('res.users', 'Assigned To',states={'approved': [('readonly', True)]}),
        'sequence_id': fields.char('Audit Sequence', size=32, required=True),
        'num_received_document': fields.char('Number of Received Documents',required = True,states={'approved': [('readonly', True)]}),
        'received_date': fields.datetime('Received date',required = True,states={'approved': [('readonly', True)]}),
        'delivered_date': fields.datetime('Delivered date',states={'approved': [('readonly', True)]}),
        'department_id': fields.many2one('hr.department','Sector', domain = [('type', '=', 'sector')],states={'approved': [('readonly', True)]}),
        'type_doc': fields.selection([('budget','Budget'),('description','Description'),('complain','Complain')], 'Document Type',states={'approved': [('readonly', True)]}),
        'doc_name': fields.text('Name',size=160,required = True,states={'approved': [('readonly', True)]}),
        'partner_id': fields.many2one('res.partner','Partner',states={'approved': [('readonly', True)]}),
        'location': fields.char('Location',states={'approved': [('readonly', True)]}),
        'received_value': fields.float('Receive Value',states={'approved': [('readonly', True)]}),
        'check_budget': fields.float('Check Budget',states={'approved': [('readonly', True)]}),
        'difference': fields.float('Difference',states={'approved': [('readonly', True)]}),
        'num_delivery_document': fields.char('Number of Delivery Documents',states={'approved': [('readonly', True)]}),
        'description': fields.text('Description',size=160,states={'approved': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'contract_num': fields.char('Contract Number',states={'approved': [('readonly', True)]}),
    }

    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'received_date': fields.datetime.now,
        'sequence_id':'/',
        'state':'draft',
    }

    def onchange_diff(self, cr, uid, ids, received_value, check_budget, difference, context=None):
        res = {}
        diff_value = ''
        if received_value and check_budget:
            diff_value = received_value - check_budget
            res.update({'difference': diff_value})

        return {'value': res}

    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.audit')
        audit = super(mak_audit, self).create(cr, uid, vals, context=context)
        return audit

    # by Тэмүүжин Батлах
    def action_approve(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'})
        return True

    # by Тэмүүжин Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def _cron_check_black_list(self, cr, uid, context=None):
        model_obj = openerp.pooler.get_pool(cr.dbname).get('ir.model.data')
        partner_obj = self.pool.get('res.partner')
        aml_obj = self.pool.get('account.move.line')
        # 56656
        partner_ids = partner_obj.search(cr,uid,[('is_blackened','=',True),('date_blackened','<>',None)])
        # partner_ids = partner_obj.search(cr, uid, [('id', '=', 56656)])
        notif_groups = model_obj.get_object_reference(cr, SUPERUSER_ID, 'mak_audit', 'group_mak_audit')
        if partner_ids:
            print 'Partner ids \n\n\n',partner_ids
            for x in partner_ids:
                pr_obj = partner_obj.browse(cr,uid,x)
                for pr in pr_obj:
                    check_aml_ids = aml_obj.search(cr, uid, [('partner_id','=',pr.id),('create_date','>=',pr.date_blackened)])
                    if check_aml_ids:
                        check_aml_obj = aml_obj.browse(cr, uid, check_aml_ids)
                        for aml in check_aml_obj:
                            data = {
                                'date': aml.date,
                                'partner_id': aml.partner_id.name,
                                'ref': aml.ref,
                                'id': aml.move_id.id,
                                'move_id': aml.move_id.name,
                                'create_uid': aml.create_uid.login,
                                'base_url': self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url'),
                                'action_id':self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account','action_move_line_form')[1],
                            }
                            if notif_groups:
                                sel_user_ids = self.pool.get('res.users').search(cr, SUPERUSER_ID,[('groups_id', 'in', [notif_groups[1]])])
                                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mak_audit','audit_email_template_to_audit')[1]
                                users = self.pool.get('res.users').browse(cr, uid, sel_user_ids)
                                user_emails = []
                                for user in users:
                                    user_emails.append(user.login)
                                    print(user.login)
                                    self.pool.get('email.template').send_mail(cr, uid, template_id, user.id, force_send = True, context=data)
                                email = u'.\n Дараах хэрэглэгчид рүү имэйл илгээгдэв: ' + (
                                    '<b>' + ('</b>, <b>'.join(user_emails)) + '</b>')
                                pr.update({
                                    'date_blackened': datetime.today().strftime('%Y-%m-%d')
                                })
                            # self.pool.get('hr.contract').message_post(cr, uid, contracts_main.id, body=email, context=None)

