# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


from openerp.osv import osv, fields, expression
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import psycopg2

import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round, float_compare

class product_product(osv.osv):
    _inherit = "product.product"

    def action_delete_data(self, cr, uid, ids, data, context=None):
        print'Code here'
        product_obj = self.pool.get('product.product')
        product_tmpl_obj = self.pool.get('product.template')
        stock_quant = self.pool.get('stock.quant')
        delete_data = product_obj.search(cr,uid,[('categ_id','=',399)],context=None)
        if delete_data:
            for x in delete_data:
                qty_s = stock_quant.search(cr,uid,[('product_id','=',x),('location_id','not in',[18])],context=None)
                if not qty_s:
                    inactive = self.pool.get('product.product').browse(cr,uid,x,context=None)
                    for item in inactive:
                        tmp = self.pool.get('product.template').search(cr,uid,[('id','=',item.product_tmpl_id.id)])
                        inactive_tmp = product_tmpl_obj.browse(cr,uid,tmp,context=context)
                        if inactive_tmp and inactive :
                            inactive_tmp.write({'active':False})
                            inactive.write({'active':False})

        return True