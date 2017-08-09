# -*- coding: utf-8 -*-
##############################################################################
#
#    Asterisk Technologies LLC, Enterprise Management Solution
#    Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn/, http://asterisk-tech.mn/&gt;). All Rights Reserved
#
#    Email : temuujintsogt@gmail.com
#    Phone : 976 + 99741074
#
##############################################################################
from openerp.osv import fields, osv
from openerp.tools.translate import _
import code


class product_template(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', select=1),
    }

    _defaults = {
        'company_id':False
    }


