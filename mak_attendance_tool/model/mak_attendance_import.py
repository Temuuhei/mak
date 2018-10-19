import logging
from openerp.osv import fields, osv
from openerp import tools, api
from datetime import datetime, timedelta
import time
import dateutil
from datetime import date
from openerp.tools.translate import _


class zk_tmp(osv.osv):
    _name = "zk.tmp"
    _description = "Tmp table of zk info"

    _columns = {
        'device_id':fields.integer('Device Number'),
        'in':fields.integer('In'),
        'out':fields.integer('Out'),
        'employee_id':fields.integer('Employee ID'),
        'inpdate':fields.datetime('Inp Datetime'),

    }


class zk_main(osv.osv):
    _name = "zk.main"
    _description = "Zk main table"

    _columns = {
        'device_id': fields.integer('Device Number'),
        'in': fields.integer('In'),
        'out': fields.integer('Out'),
        'employee_id': fields.integer('Employee ID'),
        'inpdate': fields.datetime('Inp Datetime'),

    }
