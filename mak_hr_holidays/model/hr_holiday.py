# -*- coding: utf-8 -*-
##############################################################################
#
# Mongolyn Alt LLC, Enterprise Management Solution
# Copyright (C) 2013-2015 Asterisk Technologies LLC (<http://www.erp.mn/, http://asterisk-tech.mn/&gt;). All Rights Reserved #
# Email : temuujintsogt@gmail.com
# Phone : 976 + 99741074
#
##############################################################################
import datetime
import math
import time
from operator import attrgetter

from openerp.exceptions import Warning
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools import float_compare
from openerp.tools.translate import _

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

class hr_holidays(osv.osv):
    _inherit = ['hr.holidays']
    _name = "hr.holidays"
    _description = "Leave"
    _order = "type desc, date_from asc"

    # TODO: can be improved using resource calendar method
    def _get_number_of_days(self, date_from, date_to):
        """Returns a float equals to the timedelta between two dates given as string."""

        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
        to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
        timedelta = to_dt - from_dt
        diff_day = timedelta.days + float(timedelta.seconds) / 86400
        return diff_day


    def onchange_date_from(self, cr, uid, ids, date_to, date_from):
        """
        If there are no date set for date_to, automatically set one 8 hours later than
        the date_from.
        Also update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'), _('The start date must be anterior to the end date.'))

        result = {'value': {}}

        # No date_to set so far: automatically compute one 8 hours later
        if date_from and not date_to:
            date_form_with_delta = datetime.datetime.strptime(date_from,tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=2)
            date_to_with_delta = datetime.datetime.strptime(date_from,tools.DEFAULT_SERVER_DATETIME_FORMAT) + datetime.timedelta(hours=8)
            result['value']['date_from'] = str(date_form_with_delta)
            result['value']['date_to'] = str(date_to_with_delta)
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            total = diff_day * 3
            if total <= 1.0:
                dt1 = datetime.datetime.combine(from_dt, datetime.time(12, 0))
                dt2 = datetime.datetime.combine(to_dt, datetime.time(14, 0))
                # Цайны цаг орсон эсэхийг шалгаж байна
                if from_dt < dt1 and to_dt >= dt2:
                    result['value']['number_of_days_temp'] = (diff_day * 3) - 0.1250
                else:
                    result['value']['number_of_days_temp'] = diff_day * 3
            else:
                result['value']['number_of_days_temp'] = 1
        else:
            result['value']['number_of_days_temp'] = 0
        return result

    def onchange_date_to(self, cr, uid, ids, date_to, date_from):
        """
        Update the number_of_days.
        """
        # date_to has to be greater than date_from
        if (date_from and date_to) and (date_from > date_to):
            raise osv.except_osv(_('Warning!'), _('The start date must be anterior to the end date.'))
        result = {'value': {}}
        # Compute and update the number of days
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._get_number_of_days(date_from, date_to)
            result['value']['number_of_days_temp'] = round(math.floor(diff_day)) + 1
            from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
            to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
            if from_dt.date() == to_dt.date():
                from_dt = datetime.datetime.strptime(date_from, DATETIME_FORMAT)
                to_dt = datetime.datetime.strptime(date_to, DATETIME_FORMAT)
                timedelta = to_dt - from_dt
                total = diff_day * 3
                if total <= 1.0:
                    dt1 = datetime.datetime.combine(from_dt, datetime.time(12, 0))
                    dt2 = datetime.datetime.combine(to_dt, datetime.time(14, 0))
                    # Цайны цаг орсон эсэхийг шалгаж байна
                    if from_dt < dt1 and to_dt >= dt2 :
                        result['value']['number_of_days_temp'] = (diff_day * 3) - 0.1250
                    else:
                        result['value']['number_of_days_temp'] = diff_day * 3
                else:
                    result['value']['number_of_days_temp'] = 1
        else:
            result['value']['number_of_days_temp'] = 0

        return result
