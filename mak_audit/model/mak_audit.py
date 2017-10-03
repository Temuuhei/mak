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
        'assigned_id': fields.many2one('res.users', 'Assigned To'),
        'sequence_id': fields.char('Audit Sequence', size=32, required=True),
        'num_received_document': fields.char('Number of Received Documents',required = True),
        'received_date': fields.datetime('Received date',required = True),
        'delivered_date': fields.datetime('Delivered date'),
        'department_id': fields.many2one('hr.department','Sector', domain = [('type', '=', 'sector')]),
        'type_doc': fields.selection([('budget','Budget'),('description','Description'),('complain','Complain')], 'Document Type'),
        'doc_name': fields.text('Name',size=160,required = True),
        'partner_id': fields.many2one('res.partner','Partner'),
        'location': fields.char('Location'),
        'received_value': fields.float('Receive Value'),
        'check_budget': fields.float('Check Budget'),
        'difference': fields.float('Difference'),
        'num_delivery_document': fields.char('Number of Delivery Documents'),
        'description': fields.text('Description',size=160),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'contract_num': fields.char('Contract Number'),
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
