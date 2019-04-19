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
import logging
import json
import requests
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone


_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class mak_sampler_line(osv.osv):
    _name = 'mak.sampler.line'

    _columns = {
        'in_name':fields.char('Local Name'),
        'name':fields.char('Name'),
        'weight':fields.float('Weight'),
        'sampler_id':fields.many2one('mak.sampler', 'Sampler')
    }

class mak_sampler(osv.osv):
    _name = 'mak.sampler'
    _description = "MAK TRC Labortory"
    _inherit = ['mail.thread']
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('approved', 'Approved'),]

    # Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.date, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
            args = args or []
            if name:
                ids = self.search(cr, uid, [('partner_id.name', operator, name)] + args, limit=limit, context=context or {})
                if not ids:
                    ids = self.search(cr, uid, [('type', operator, name)] + args, limit=limit, context=context or {})
            else:
                ids = self.search(cr, uid, args, limit=limit, context=context or {})
            return self.name_get(cr, uid, ids, context or {})

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=None):
            res.append( (doc.id, u'[%s] [%s] [%s]' % (doc.sequence_id, doc.partner_id.name,doc.location)))
        return res


    _columns = {
        'user_id': fields.many2one('res.users', 'Employee', required=True, readonly=True),
        'sequence_id': fields.char('Sampler Sequence', size=32, required=True),
        'partner_id': fields.many2one('res.partner', 'Partner', required=True,states={'approved': [('readonly', True)]}),
        'date': fields.datetime('Received date',required = True,states={'approved': [('readonly', True)]}),
        'location': fields.char('Location',states={'approved': [('readonly', True)]}),
        'type': fields.char('Type',states={'approved': [('readonly', True)]}),
        'partner_num': fields.char('Partner Number',states={'approved': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'qty': fields.float('Quantity', states={'approved': [('readonly', True)]}, track_visibility='onchange',required=True),
        'line_qty': fields.integer(' ', states={'approved': [('readonly', True)]}, track_visibility='onchange',required=True),
        'pure_weight': fields.float('Weight', states={'approved': [('readonly', True)]}, track_visibility='onchange'),
        'is_duplicate': fields.boolean('Is Duplicate', states={'approved': [('readonly', True)]}, track_visibility='onchange'),
        'is_analytic': fields.boolean('Is Analytic', states={'approved': [('readonly', True)]}, track_visibility='onchange'),
        'line_id':fields.one2many('mak.sampler.line','sampler_id','Line', copy = True),
        'lab_id': fields.many2one('mak.labortory', 'Labortory', states={'approved': [('readonly', True)]}),
        'continue_seq':fields.boolean('Is continue'),
        'last_seq': fields.related('lab_id', 'last_seq',
                                       type='char', relation='mak.labortory', string='Last Sequence'),
        'last_sample_num': fields.related('lab_id', 'last_sample_num',
                                   type='integer', relation='mak.labortory', string='Last Sample num'),
    }


    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'date': fields.datetime.now,
        'sequence_id':'/',
        'state':'draft',
    }


    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.sampler')
        audit = super(mak_sampler, self).create(cr, uid, vals, context=context)
        return audit

    # by Тэмүүжин Батлах
    def action_approve(self, cr, uid, ids, context=None):
        last_seq = 0.0
        obj = self.browse(cr, uid, ids)[0]
        last_seq = obj.lab_id.last_sample_num
        obj.lab_id.write({'last_sample_num': last_seq + int(len(obj.line_id))})
        self.write(cr, uid, ids, {'state': 'approved'})
        return True

    # by Тэмүүжин Цуцлах
    def action_draft(self, cr, uid, ids, context=None):
        last_seq = 0.0
        obj = self.browse(cr, uid, ids)[0]
        last_seq = obj.lab_id.last_sample_num
        obj.lab_id.write({'last_sample_num': last_seq - int(len(obj.line_id))})
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    #by Тэмүүжин тоо хэмжээг хуваах
    def action_generate(self,cr,uid,ids,context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        if obj.partner_num and obj.pure_weight and not obj.continue_seq:
            cr.execute('Delete from mak_sampler_line where sampler_id=%s',
                       (obj.id,))
            if obj.lab_id.short_name and obj.lab_id.last_seq and obj.lab_id.last_sample_num:
                i = 1
                while i <= obj.line_qty:
                    print(i)

                    data = {
                        'in_name': obj.lab_id.short_name + '-' + obj.lab_id.last_seq + '-' + str(
                            obj.lab_id.last_sample_num + i),
                        'name': obj.partner_num + '-' + str(i),
                        'weight': obj.pure_weight / obj.line_qty,
                        'sampler_id': obj.id}
                    m_line_ids = self.pool.get('mak.sampler.line').create(cr, uid, data, context=context)
                    i += 1
            else:
                raise osv.except_osv(_('Warning!'),
                                     _(u"ТА лаборторын богино нэр, дараалал, хамгийн сүүлийн дугаар гэх талбаруудыг бөглөнө үү!! "))
        else:
            print 'Temka'
            if obj.lab_id.short_name and obj.lab_id.last_seq and obj.lab_id.last_sample_num:
                i = 1
                while i <= obj.line_qty:
                    print(i)
                    data = {
                        'in_name': obj.lab_id.short_name + '-' + obj.lab_id.last_seq + '-' + str(obj.lab_id.last_sample_num + i),
                        'name': obj.partner_num + '-' + str(i),
                        'weight': obj.pure_weight / obj.line_qty,
                        'sampler_id': obj.id}
                    m_line_ids = self.pool.get('mak.sampler.line').create(cr, uid, data, context=context)
                    i += 1
            else:
                raise osv.except_osv(_('Warning!'),
                                     _(
                                         u"ТА лаборторын богино нэр, дараалал, хамгийн сүүлийн дугаар гэх талбаруудыг бөглөнө үү!! "))
        return True

class mak_labortory(osv.osv):
    _name = 'mak.labortory'
    _description = "MAK TRC Labortory"
    _inherit = ['mail.thread']

    _columns = {
           'name':fields.char('Name'),
           'short_name':fields.char('Short Name'),
           'last_seq':fields.char('Sequence'),
           'last_sample_num':fields.integer('Last Sample Number')

       }

class mak_research_line(osv.osv):
    _name = 'mak.research.line'

    _columns = {
        'product_id':fields.many2one('product.product','Product'),
        # 'sampler_process':fields.float('Sampler Process'),
        # 'sampler_prepare':fields.float('Sampler Prepare'),
        # 'sampler_research':fields.float('Research'),
        'tax_id': fields.many2many('account.tax', 'mak_sampler_tax', 'order_line_id', 'tax_id', 'Taxes'),
        'weight':fields.float('Weight'),
        'qty':fields.float('Quant'),
        # 'total':fields.float('Total'),
        'research_id':fields.many2one('mak.research', 'Research')
    }

    # def onchange_total(self, cr, uid, ids, sampler_process, sampler_prepare, sampler_research,total, context=None):
    #     res={}
    #     if sampler_process or sampler_prepare or sampler_research:
    #         total =sampler_process + sampler_prepare + sampler_research
    #         res.update({'total': total})
    #
    #     return {'value':res}

class sale_order(osv.osv):
    _inherit = 'sale.order'

    _columns = {
        'mak_research_id' : fields.many2one('mak.research', 'Research')
    }

class mak_research(osv.osv):
    _name = 'mak.research'
    _description = "MAK TRC Research"
    _inherit = ['mail.thread']
    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sale_order_created', 'Sale order created'),]

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for doc in self.browse(cr, uid, ids, context=None):
            res.append((doc.id, u'[%s] [%s] [%s]' % (doc.sequence_id, doc.lab_id.name, doc.research_type)))
        return res

    # Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.deadline, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def _get_warehouse(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return (user.allowed_warehouses and map(lambda x: x.id, user.allowed_warehouses))[0] or 0


    _columns = {
        'user_id': fields.many2one('res.users', 'Employee', required=True, readonly=True),
        'sequence_id': fields.char('Research Sequence', size=32, required=True),
        'partner_id': fields.related('sampler_id','partner_id', string ='Partner', type='many2one', relation = 'res.partner', readonly=True),
        'date': fields.related('sampler_id','date',string='Received date', type='datetime', relation='mak.sampler', readonly=True),
        'element_union': fields.char('Element Union', states={'approved': [('readonly', True)]}),
        'deadline': fields.datetime('Deadline', required=True, states={'approved': [('readonly', True)]}),
        'location': fields.related('sampler_id','location',string ='Location',  type ='char', relation='mak.sampler', readonly=True),
        'research_type': fields.char('Research Type', states={'approved': [('readonly', True)]}),
        'type': fields.related('sampler_id','type',string ='Type', type ='char', relation='mak.sampler', readonly=True),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection(STATE_SELECTION, 'State', readonly=True, track_visibility='onchange'),
        'qty': fields.related('sampler_id','qty',string ='Quantity', type ='float', relation='mak.sampler', readonly=True),
        'pure_weight': fields.related('sampler_id','pure_weight',string ='Weight', type ='float', relation='mak.sampler', readonly=True),
        'is_duplicate': fields.related('sampler_id','is_duplicate',string ='Is Duplicate', type ='boolean', relation='mak.sampler', readonly=True
                                      ),
        'is_analytic': fields.related('sampler_id','is_analytic',string ='Is Analytic', type ='boolean', relation='mak.sampler', readonly=True,
                                     ),
        'sampler_id': fields.many2one('mak.sampler', 'Sampler', states={'approved': [('readonly', True)]}),
        'lab_id': fields.many2one('mak.labortory', 'Labortory', states={'approved': [('readonly', True)]}),
        'sale_category': fields.many2one('sale.category', 'Category', required=True),
        'pricelist_id': fields.many2one('product.pricelist', 'Pricelist', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]},
                                        help="Pricelist for current sales order."),
        'currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency",
                                      string="Currency", readonly=True, required=True),
        'line_id': fields.one2many('mak.research.line', 'research_id', 'Line', copy=True),
        'warehouse_id': fields.many2one('stock.warehouse', 'Warehouse', copy=False),
        'sale_order': fields.many2one('sale.order', 'Sale Order', copy=False),
    }
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'warehouse_id': _get_warehouse,
        'sequence_id': '/',
        'state': 'draft',
    }



    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, line_id, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        value = {
            'currency_id': self.pool.get('product.pricelist').browse(cr, uid, pricelist_id,
                                                                     context=context).currency_id.id
        }
        if not line_id or line_id == [(6, 0, [])]:
            return {'value': value}
        warning = {
            'title': _('Pricelist Warning!'),
            'message': _(
                'If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning, 'value': value}

    def create (self, cr, uid, vals, context=None):
        vals['sequence_id'] = self.pool.get('ir.sequence').get(cr, uid, 'mak.research')
        audit = super(mak_research, self).create(cr, uid, vals, context=context)
        return audit

    def print_report(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        raise osv.except_osv(_('Warning!'),
                             _(u"Хэвлэх хөгжүүлэлт хийгдэж байна"))
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        self.signal_workflow(cr, uid, ids, 'quotation_sent')
        return self.pool['report'].get_action(cr, uid, ids, 'sale.report_saleorder', context=context)

    # by Тэмүүжин Батлах
    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def action_approve(self, cr, uid, ids,context=None):
        obj = self.browse(cr, uid, ids, context=context)
        if obj.sale_order:
            raise osv.except_osv(_('Warning!'), _(u"Та эхлээд холбоотой борлуулалтын захиалга /Үнийн санал/ устгах шаардлагатай!"))

        if obj.deadline:
            sale_order = self.pool.get('sale.order').create(cr,uid,
                {'date_order': obj.deadline,
                 'requested_date': obj.deadline,
                 'partner_id': obj.partner_id.id,
                 'pricelist_id': obj.pricelist_id.id,
                 'order_policy': 'manual',
                 'picking_policy': 'one',
                 'warehouse_id': obj.warehouse_id.id,
                 'sale_category_id': obj.sale_category.id,
                 'origin': obj.sequence_id})

            total_qty = 0
            lines = []

            if obj.warehouse_id.analytic_share_id:
                for share in obj.warehouse_id.analytic_share_id:
                    line = {'analytic_account_id': share.analytic_account_id.id,
                            'rate': share.rate or 0
                            }

                    lines += [(0, 0, line)]
            else:
                raise osv.except_osv(_('Warning!'),
                                     _(u"Та эхлээд агуулахын бүртгэлийн шинжилгээний хуваарилалт талбарыг бүртгэх шаардлагатай!"))
            if obj.line_id:
                for l in obj.line_id:
                    total_qty += l.qty

                    self.pool.get('sale.order.line').create(cr,uid,{
                        'product_uom': l.product_id.uom_id.id,
                        'product_uom_qty': total_qty,
                        'product_id': l.product_id.id,
                        'delay': 0,
                        'order_partner_id': obj.partner_id.id,
                        'order_id': sale_order,
                        'analytic_share_id': lines
                    })

            if sale_order:
                print 'SAle order \n\n',sale_order
                obj.write({'sale_order': sale_order, 'state': 'sale_order_created'})
                self.pool.get('sale.order').write(cr, uid, sale_order, {'mak_research_id': obj.id,
                                                                         },
                                                      context=context)
            return True


