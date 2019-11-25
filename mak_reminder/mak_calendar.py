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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date
from dateutil import parser
from openerp import SUPERUSER_ID
from openerp.http import request
from lxml import etree
from openerp import tools, SUPERUSER_ID
import datetime
from datetime import timedelta

_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"

def calendar_id2real_id(calendar_id=None, with_date=False):
    """
    Convert a "virtual/recurring event id" (type string) into a real event id (type int).
    E.g. virtual/recurring event id is 4-20091201100000, so it will return 4.
    @param calendar_id: id of calendar
    @param with_date: if a value is passed to this param it will return dates based on value of withdate + calendar_id
    @return: real event id
    """
    if calendar_id and isinstance(calendar_id, (basestring)):
        res = calendar_id.split('-')
        if len(res) >= 2:
            real_id = res[0]
            if with_date:
                real_date = time.strftime(DEFAULT_SERVER_DATETIME_FORMAT, time.strptime(res[1], "%Y%m%d%H%M%S"))
                start = datetime.strptime(real_date, DEFAULT_SERVER_DATETIME_FORMAT)
                end = start + timedelta(hours=with_date)
                return (int(real_id), real_date, end.strftime(DEFAULT_SERVER_DATETIME_FORMAT))
            return int(real_id)
    return calendar_id and int(calendar_id) or calendar_id

class calendar_attendee(osv.Model):
    """
    Calendar Attendee Information
    """
    _inherit = 'calendar.attendee'

    def _send_mail_to_attendees(self, cr, uid, ids, email_from=tools.config.get('email_from', False),
                                template_xmlid='calendar_template_meeting_invitation', force=True, context=None):
        """
        Send mail for event invitation to event attendees.
        @param email_from: email address for user sending the mail
        @param force: If set to True, email will be sent to user himself. Usefull for example for alert, ...
        """
        res = False
        if self.pool['ir.config_parameter'].get_param(cr, uid, 'calendar.block_mail', default=False) or context.get("no_mail_to_attendees"):
            return res

        mail_ids = []
        data_pool = self.pool['ir.model.data']
        mailmess_pool = self.pool['mail.message']
        mail_pool = self.pool['mail.mail']
        template_pool = self.pool['email.template']
        local_context = context.copy()
        color = {
            'needsAction': 'grey',
            'accepted': 'green',
            'tentative': '#FFFF00',
            'declined': 'red'
        }

        if not isinstance(ids, (tuple, list)):
            ids = [ids]

        dummy, template_id = data_pool.get_object_reference(cr, uid, 'calendar', template_xmlid)
        dummy,new_template_id = data_pool.get_object_reference(cr, uid, 'mak_reminder', 'calendar_template_meeting_invitation_mak1')
        dummy, act_id = data_pool.get_object_reference(cr, uid, 'calendar', "view_calendar_event_calendar")
        local_context.update({
            'color': color,
            'action_id': self.pool['ir.actions.act_window'].search(cr, uid, [('view_id', '=', act_id)], context=context)[0],
            'dbname': cr.dbname,
            'base_url': self.pool['ir.config_parameter'].get_param(cr, uid, 'web.base.url', default='http://localhost:8069', context=context)
        })

        for attendee in self.browse(cr, uid, ids, context=context):
            if attendee.email and email_from and (attendee.email != email_from or force):
                ics_file = self.get_ics_file(cr, uid, attendee.event_id, context=context)
                if new_template_id:
                    mail_id = template_pool.send_mail(cr, uid, new_template_id, attendee.id, context=local_context)
                else:
                    mail_id = template_pool.send_mail(cr, uid, template_id, attendee.id, context=local_context)
                vals = {}
                if ics_file:
                    vals['attachment_ids'] = [(0, 0, {'name': 'invitation.ics',
                                                      'datas_fname': 'invitation.ics',
                                                      'datas': str(ics_file).encode('base64')})]
                vals['model'] = None  # We don't want to have the mail in the tchatter while in queue!
                vals['res_id'] = False
                the_mailmess = mail_pool.browse(cr, uid, mail_id, context=context).mail_message_id
                mailmess_pool.write(cr, uid, [the_mailmess.id], vals, context=context)
                mail_ids.append(mail_id)

        if mail_ids:
            res = mail_pool.send(cr, uid, mail_ids, context=context)

        return res

class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'


    def create_attendees(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        user_obj = self.pool['res.users']
        current_user = user_obj.browse(cr, uid, uid, context=context)
        res = {}
        for event in self.browse(cr, uid, ids, context):
            attendees = {}
            for att in event.attendee_ids:
                attendees[att.partner_id.id] = True
            new_attendees = []
            new_att_partner_ids = []
            for partner in event.partner_ids:
                if partner.id in attendees:
                    continue
                access_token = self.new_invitation_token(cr, uid, event, partner.id)
                values = {
                    'partner_id': partner.id,
                    'event_id': event.id,
                    'access_token': access_token,
                    'email': partner.email,
                }

                if partner.id == current_user.partner_id.id:
                    values['state'] = 'accepted'
                att_id = self.pool['calendar.attendee'].create(cr, uid, values, context=context)
                new_attendees.append(att_id)
                new_att_partner_ids.append(partner.id)


                if not current_user.email or current_user.email != partner.email:
                    mail_from = current_user.email or tools.config.get('email_from', False)
                    if not context.get('no_email'):
                        if self.pool['calendar.attendee']._send_mail_to_attendees(cr, uid, att_id, email_from=mail_from, context=context):
                            self.message_post(cr, uid, event.id, body=_("An invitation email has been sent to attendee %s") % (partner.name,), subtype="calendar.subtype_invitation", context=context)

            if new_attendees:
                self.write(cr, uid, [event.id], {'attendee_ids': [(4, att) for att in new_attendees]}, context=context)
            if new_att_partner_ids:
                self.message_subscribe(cr, uid, [event.id], new_att_partner_ids, context=context)

            # We remove old attendees who are not in partner_ids now.
            all_partner_ids = [part.id for part in event.partner_ids]
            all_part_attendee_ids = [att.partner_id.id for att in event.attendee_ids]
            all_attendee_ids = [att.id for att in event.attendee_ids]
            partner_ids_to_remove = map(lambda x: x, set(all_part_attendee_ids + new_att_partner_ids) - set(all_partner_ids))

            attendee_ids_to_remove = []

            if partner_ids_to_remove:
                attendee_ids_to_remove = self.pool["calendar.attendee"].search(cr, uid, [('partner_id.id', 'in', partner_ids_to_remove), ('event_id.id', '=', event.id)], context=context)
                if attendee_ids_to_remove:
                    self.pool['calendar.attendee'].unlink(cr, uid, attendee_ids_to_remove, context)

            res[event.id] = {
                'new_attendee_ids': new_attendees,
                'old_attendee_ids': all_attendee_ids,
                'removed_attendee_ids': attendee_ids_to_remove
            }
        return res

    def write(self, cr, uid, ids, values, context=None):
        context = context or {}
        if not isinstance(ids, (tuple, list)):
            ids = [ids]

        values0 = values

        # process events one by one
        for event_id in ids:
            # make a copy, since _set_date() modifies values depending on event
            values = dict(values0)
            self._set_date(cr, uid, values, event_id, context=context)

            # special write of complex IDS
            real_ids = []
            new_ids = []
            if '-' not in str(event_id):
                real_ids = [int(event_id)]
            else:
                real_event_id = calendar_id2real_id(event_id)

                # if we are setting the recurrency flag to False or if we are only changing fields that
                # should be only updated on the real ID and not on the virtual (like message_follower_ids):
                # then set real ids to be updated.
                blacklisted = any(key in values for key in ('start', 'stop', 'active'))
                if not values.get('recurrency', True) or not blacklisted:
                    real_ids = [real_event_id]
                else:
                    data = self.read(cr, uid, event_id, ['start', 'stop', 'rrule', 'duration'])
                    if data.get('rrule'):
                        new_ids = [self._detach_one_event(cr, uid, event_id, values, context=None)]

            super(calendar_event, self).write(cr, uid, real_ids, values, context=context)

            # set end_date for calendar searching
            if any(field in values for field in ['recurrency', 'end_type', 'count', 'rrule_type', 'start', 'stop']):
                for event in self.browse(cr, uid, real_ids, context=context):
                    if event.recurrency and event.end_type in ('count', unicode('count')):
                        final_date = self._get_recurrency_end_date(cr, uid, event.id, context=context)
                        super(calendar_event, self).write(cr, uid, [event.id], {'final_date': final_date}, context=context)

            attendees_create = False
            if values.get('partner_ids', False):
                attendees_create = self.create_attendees(cr, uid, real_ids + new_ids, context)

            if (values.get('start_date') or values.get('start_datetime')) and values.get('active', True):
                for the_id in real_ids + new_ids:
                    if attendees_create:
                        attendees_create = attendees_create[the_id]
                        mail_to_ids = list(set(attendees_create['old_attendee_ids']) - set(attendees_create['removed_attendee_ids']))
                    else:
                        mail_to_ids = [att.id for att in self.browse(cr, uid, the_id, context=context).attendee_ids]

                    if mail_to_ids:
                        current_user = self.pool['res.users'].browse(cr, uid, uid, context=context)
                        if self.pool['calendar.attendee']._send_mail_to_attendees(cr, uid, mail_to_ids, template_xmlid='mak_reminder.calendar_template_meeting_invitation_mak', email_from=current_user.email, context=context):
                            self.message_post(cr, uid, the_id, body=_("A email has been send to specify that the date has been changed !"), subtype="calendar.subtype_invitation", context=context)

        return True

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        self._set_date(cr, uid, vals, id=False, context=context)
        if not 'user_id' in vals:  # Else bug with quick_create when we are filter on an other user
            vals['user_id'] = uid
        res = super(calendar_event, self).create(cr, uid, vals, context=context)
        final_date = self._get_recurrency_end_date(cr, uid, res, context=context)
        self.write(cr, uid, [res], {'final_date': final_date}, context=context)
        self.create_attendees(cr, uid, [res], context=context)
        return res
