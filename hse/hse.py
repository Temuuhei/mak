# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014-today MNO LLC (<http://www.mno.mn>)
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

from openerp.osv import fields, osv
from datetime import datetime, timedelta
from openerp.tools.translate import _
from openerp.http import request
from openerp import http
from openerp.http import request

import pytz


class hse(http.Controller):

    @http.route('/get_hse_rules', type='json', auth='user')
    def get_hse_rules(self):
        hse_rules = []
        hse_rules_name = request.env['hse.rules.documents.name'].search([])
        for name in hse_rules_name:
            hse_rules_recs = request.env['hse.rules.documents'].search([('name_id', '=', name.id)])
            vals = {
                'rule name': name.name,
                'notes': [{
                    'id': rec.id,
                    'number': rec.number,
                    'title': rec.title,
                    'subject': rec.subject,
                    'rules': [{
                        'description': desc.description
                    } for desc in
                        request.env['hse.rules.documents.description'].search([('description_id', '=', rec.id)])]
                } for rec in hse_rules_recs]
            }
            hse_rules.append(vals)
        if hse_rules:
            data = {'status': 200, 'response': hse_rules, 'message': 'Done All Hse Rules Returned'}
        else:
            data = {'status': 200, 'response': hse_rules, 'message': 'Hse Rules not found'}
        return data

    @http.route('/get_hr_user', type='json', auth='user')
    def get_hr_user(self, **rec):
        if request.jsonrequest:
            if rec['user_id']:
                roles = []
                role = 0
                user = request.env['hr.employee'].search([('resource_id.user_id', '=', rec['user_id'])])
                job = request.env['hr.job.classification'].search([])
                for i in job:
                    if i.id == 6 or i.id == 7:
                        roles.append(i.id)
                if user:
                    if user.job_classification.id in roles:
                        role =1
                    else:
                        role =0
                    vals = {
                        'uid': user.user_id.id,
                        'UserName': user.user_id.name,
                        'email': user.user_id.login,
                        'office':user.job_id.name,
                        'image': "https://erp.mak.mn/web/binary/image?model=res.users&id="+str(user.user_id.id)+"&field=image_medium",
                        'role': role,
                        'company': user.company_id.name
                        # 'runtime': rec['shipment_amount'],
                    }
                    data = {'status': True, 'message': "MAK ERP", 'response': vals}
                else:
                    data = {'status': False, 'message': "MAK ERP",
                                'response': "Ажилтан олдсонгүй"}
            else:
                data = {'status': False, 'message': "MAK ERP", 'response': "Харилцагч хоорондын зайг оруулна уу"}
            return data

class hse_safety_plan(osv.osv):
    _name = 'hse.safety.plan'
    _description = 'Safety plan'
    _inherit = ["mail.thread"]

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        res[obj.id] = obj.year
        return res

    def _set_percent(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        per = 0
        if int(obj.actual):
            if obj.is_count:
                per = (100 * int(obj.actual)) / obj.count
                if per > 100:
                    per = 100
            elif int(obj.actual) > 100:
                per = 100
            else:
                per = obj.actual
        res[obj.id] = per
        # else:
        #     raise osv.except_osv(_('Error'), _('Actual is count!!!'))

        return res

    _columns = {
        'name': fields.function(_set_name, type='char', string='Name', readonly=True),
        'year': fields.selection(
            [('2012', '2012'), ('2013', '2013'), ('2014', '2014'), ('2015', '2015'), ('2016', '2016'), ('2017', '2017'),
             ('2018', '2018'), ('2019', '2019'), ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('', ''),
             ('', '')], 'Year', required=True),
        'indicator_id': fields.many2one('hse.safety.indicator', 'Indicator', required=True),
        'indicator_type': fields.related('indicator_id', 'type', type='selection',
                                         selection=[('leading', 'Leading indicators'),
                                                    ('lagging', 'Lagging indicators'), ('training', 'Training'),
                                                    ('env', 'Env')],
                                         string='Indicator type', readonly=True, store=True),
        'frequency': fields.selection(
            [('season_1', 'Season 1'), ('season_2', 'Season 2'), ('season_3', 'Season 3'), ('season_4', 'Season 4')],
            'Frequency', required=True),
        'is_count': fields.boolean('Is count'),
        'count': fields.integer('Count'),
        'percent': fields.integer('Percent %', group_operator='avg'),
        'actual': fields.char('Actual', size=4),
        'actual_percent': fields.function(_set_percent, type='integer', string='Actual percent %', readonly=True,
                                          group_operator='avg', store=True),
    }

    def write(self, cr, uid, ids, vals, context=None):
        if 'is_count' in vals:
            if vals['is_count']:
                vals['percent'] = 0
            else:
                vals['count'] = 0
        return super(hse_safety_plan, self).write(cr, uid, ids, vals, context=context)

    _defaults = {
        'is_count': True,
        'actual': '0'
    }
    _order = 'year asc, indicator_id desc, frequency asc'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(year, indicator_id, frequency)', 'Year and Indicator and Frequency must be unique!')
    ]


class hse_safety_indicator(osv.osv):
    _name = 'hse.safety.indicator'
    _description = 'Safety indicator'
    _columns = {
        'name': fields.char('Name', size=100, required=True),
        'type': fields.selection(
            [('leading', 'Leading indicators'), ('lagging', 'Lagging indicators'), ('training', 'Training'),
             ('env', 'Env')], 'Type', required=True),
        'value': fields.char('Value', size=30, required=True),
    }


class hse_nope_lti(osv.osv):
    _name = 'hse.nope.lti'
    _description = 'Man/Hour without LTI'
    _inherit = ["mail.thread"]

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        res[obj.id] = obj.project_id.name + ' ' + obj.date
        return res

    def _sum_man_hour(self, cr, uid, ids, name, args, context=None):
        res = {}
        m_hour = 0;
        obj = self.browse(cr, uid, ids)[0]
        for item in obj.line_ids:
            m_hour += item.man_hour
        res[obj.id] = str(m_hour)
        return res

    def _total_man_hour(self, cr, uid, ids, name, args, context=None):
        res = {}

        hour = 0
        day = 0
        cr.execute(
            "select max(h1.date),min(h1.date) from hse_nope_lti h1 where h1.date>=(select max(h2.date) from hse_nope_lti h2 where h2.man_hour='0' and h2.project_id=h1.project_id)");
        str_cr = cr.fetchone()
        print
        'str_cr  \n', str_cr
        if str_cr[0] <> None and str_cr[1] <> None:
            day = (datetime.strptime(str_cr[0], '%Y-%m-%d') - datetime.strptime(str_cr[1], '%Y-%m-%d')).days

        # cr.execute("select sum(man_hour::integer) from hse_nope_lti h1 where h1.date>=(select max(h2.date) from hse_nope_lti h2 where h2.man_hour='0' and h2.project_id=h1.project_id)");
        # hour = int(cr.fetchone()[0])
        for item in self.browse(cr, uid, self.search(cr, uid, [])):
            res[item.id] = {
                'total_man_hour': hour,
                'total_day': day,
            }
        return res

    def _inc_man_hour(self, cr, uid, ids, name, args, context=None):
        res = {}
        lti_date = False
        # obj_this = self.browse(cr, uid,ids)[0]
        for obj_this in self.browse(cr, uid, self.search(cr, uid, [])):
            lti_date = False
            for item in self.browse(cr, uid, self.search(cr, uid, [('project_id', '=', obj_this.project_id.id),
                                                                   ('man_hour', '=', '0'),
                                                                   ('date', '<=', obj_this.date)])):
                if not lti_date:
                    lti_date = item.date
                else:
                    if lti_date < item.date:
                        lti_date = item.date
            if lti_date:
                hour = 0
                day = 0
                max_date = lti_date
                for item in self.browse(cr, uid, self.search(cr, uid, [('project_id', '=', obj_this.project_id.id),
                                                                       ('date', '>=', lti_date),
                                                                       ('date', '<=', obj_this.date)])):
                    hour += int(item.man_hour)

                day = (datetime.strptime(obj_this.date, '%Y-%m-%d') - datetime.strptime(lti_date, '%Y-%m-%d')).days
                res[obj_this.id] = {
                    'inc_man_hour': str(hour),
                    'inc_total_day': str(day),
                }

        return res

    # by Bayasaa Өдөрөөр салгах
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

    _columns = {
        'date': fields.date('Date', required=True),
        'name': fields.function(_set_name, type='char', string='Name', readonly=True),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'line_ids': fields.one2many('hse.nope.lti.line', 'nope_lti_id', 'Nope lti line'),
        'man_hour': fields.function(_sum_man_hour, type='char', string='Man hour',
                                    store={'hse.nope.lti': (lambda self, cr, uid, ids, c={}: ids, [], 20), }),
        'total_man_hour': fields.function(_total_man_hour, type='integer', string='Total man hour', multi='lti',
                                          store={'hse.nope.lti': (lambda self, cr, uid, ids, c={}: ids, [], 30), },
                                          group_operator='max'),
        'total_day': fields.function(_total_man_hour, type='integer',
                                     string='Since the date registered lost time injury', multi='lti',
                                     store={'hse.nope.lti': (lambda self, cr, uid, ids, c={}: ids, [], 30), },
                                     group_operator='max'),
        'inc_total_day': fields.function(_inc_man_hour, type='char',
                                         string='Increase since the date registered lost time injury', multi='inc_lti',
                                         store={'hse.nope.lti': (lambda self, cr, uid, ids, c={}: ids, [], 30), }),
        'inc_man_hour': fields.function(_inc_man_hour, type='char', string='Increase man hour', multi='inc_lti',
                                        store={'hse.nope.lti': (lambda self, cr, uid, ids, c={}: ids, [], 30), }),
    }
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(project_id, date)', 'Project and Date must be unique!')
    ]
    _defaults = {
        'date': fields.date.context_today,
    }
    _order = 'date desc'


class hse_nope_lti_line(osv.osv):
    _name = 'hse.nope.lti.line'
    _description = 'Nope lti line'

    def _man_hour(self, cr, uid, ids, name, args, context=None):
        res = {}
        m_hour = 0;
        obj = self.browse(cr, uid, ids)[0]
        pr_hr = self.pool.get('hse.project.man.hour').search(cr, uid,
                                                             [('project_id', '=', obj.nope_lti_id.project_id.id)])
        pr = self.pool.get('hse.project.man.hour').browse(cr, uid, pr_hr)[0]
        obj = self.browse(cr, uid, ids)[0]
        res[obj.id] = obj.man * pr.man_hour
        return res

    _columns = {
        'nope_lti_id': fields.many2one('hse.nope.lti', 'Nope lti ID', required=True),
        'location_id': fields.many2one('hse.location', 'Location'),
        'man': fields.integer('Man', required=True),
        'man_hour': fields.function(_man_hour, type='integer', string='Man hour', store=True),
    }


class hse_project_man_hour(osv.osv):
    _name = 'hse.project.man.hour'
    _description = 'Project man hour'
    _columns = {
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'man_hour': fields.integer('Man hour'),
    }


class hse_safety_meeting(osv.osv):
    _name = 'hse.safety.meeting'
    _description = 'Safety meeting'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
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

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        if obj.name:
            return res
        my_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hse.safety.meeting')])[0]
        conf_ids = self.pool.get('hse.code.config').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                     ('model_id', '=', my_id)])
        if conf_ids:
            num_name = self.pool.get('hse.code.config').browse(cr, uid, conf_ids)[0].name
            max_count = 0
            cr.execute('SELECT id FROM hse_safety_meeting where project_id = %s and EXTRACT(YEAR FROM date) = %s ',
                       (obj.project_id.id, datetime.strptime(obj.date, '%Y-%m-%d').year))
            obj_ids = map(lambda x: x[0], cr.fetchall())
            for item in self.pool.get('hse.safety.meeting').browse(cr, uid, obj_ids, context=context):
                s = item.name
                if s and int(s[len(num_name): len(s)]) > max_count:
                    max_count = int(s[len(num_name): len(s)])
            res[obj.id] = num_name + str(max_count + 1).zfill(4)
            return res
        return res

    def _sum_count(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        res[obj.id] = len(
            self.pool.get('hse.safety.meeting.line').search(cr, uid, [('safety_meeting_id', '=', obj.id)]))
        return res

    def _get_line(self, cr, uid, entry_ids, context=None):
        entry = self.pool.get('hse.safety.meeting.line').browse(cr, uid, entry_ids, context=context)
        res_id = []
        for item in entry:
            res_id.append(item.safety_meeting_id.id)
        return res_id

    _columns = {
        'date': fields.date('Date', required=True, states={'done': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done')], 'State', readonly=True,
                                  track_visibility='onchange'),
        'part': fields.selection([('a', 'A'), ('b', 'B'), ('c', 'C')], 'Part', required=True,
                                 states={'done': [('readonly', True)]}),
        'name': fields.function(_set_name, type='char', string='Number', readonly=True, store=True),
        'project_id': fields.many2one('project.project', 'Project', required=True,
                                      states={'done': [('readonly', True)]}),
        'monitoring_user_id': fields.many2one('res.users', 'Monitoring user', required=True,
                                              states={'done': [('readonly', True)]}),
        'department_id': fields.many2one('hr.department', 'Department', required=True,
                                         states={'done': [('readonly', True)]}),
        'participants_count': fields.function(_sum_count, type='integer', string='Participants count',
                                              store={
                                                  'hse.safety.meeting': (lambda self, cr, uid, ids, c={}: ids, [], 20),
                                                  'hse.safety.meeting.line': (_get_line, ['participant_id'], 20)}),
        'subject': fields.char('Safety meeting subject', required=True, size=150,
                               states={'done': [('readonly', True)]}),
        'managing_employee_ids': fields.many2many('hr.employee', 'hse_safety_meeting_employee_rel', 'safety_meeting_id',
                                                  'employee_id', 'Managing employee',
                                                  states={'done': [('readonly', True)]}),

        'safety_meeting_1': fields.text('safety_meeting_1', states={'done': [('readonly', True)]}),
        'safety_meeting_2': fields.text('safety_meeting_2', states={'done': [('readonly', True)]}),
        'comment': fields.text('Comment', states={'done': [('readonly', True)]}),
        'attachment_ids': fields.many2many('ir.attachment', 'hse_safety_meeting_ir_attachments_rel',
                                           'safety_meeting_id', 'attachment_id', 'Attachments',
                                           states={'done': [('readonly', True)]}),
        'meeting_line': fields.one2many('hse.safety.meeting.line', 'safety_meeting_id', 'Safety meeting line'),
    }

    def action_to_done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def import_participants(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        line_ids = self.pool.get('hse.safety.meeting.line').search(cr, uid, [('safety_meeting_id', '=', obj.id)])
        if obj.meeting_line:
            sup_id = self.pool.get('hse.safety.meeting.line').unlink(cr, uid, line_ids, context=context)

        line_ids = []
        hr_project = self.pool.get('hr.department').search(cr, uid, [('project_id', '=', obj.project_id.id)])
        relay_id = self.pool.get('work.schedule.relay').search(cr, uid, [('relay', '=', obj.part.upper()),
                                                                         ('project_id', 'in', hr_project)])
        hr_table_ids = self.pool.get('time.table.details').search(cr, uid, [
            ('employee_state', 'in', ['work_at_night', 'work_at_day']), ('project_id', 'in', hr_project),
            ('relay', 'in', relay_id), ('department_id', '=', obj.department_id.id),
            ('date', '=', (datetime.strptime(obj.date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')),
            ('date', '<=', (datetime.strptime(obj.date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d'))])
        hr_empolyees = []

        for item in self.pool.get('time.table.details').browse(cr, uid, hr_table_ids):
            if item.employee_id.id not in hr_empolyees:
                hr_empolyees.append(item.employee_id.id)
                data = {'safety_meeting_id': obj.id,
                        'participant_id': item.employee_id.id,
                        }
                line_id = self.pool.get('hse.safety.meeting.line').create(cr, uid, data, context=context)

        line_ids = self.pool.get('hse.safety.meeting.line').search(cr, uid, [('safety_meeting_id', '=', obj.id)])

        return {
            'value': {
                'meeting_line': line_ids
            }
        }

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
        'monitoring_user_id': lambda obj, cr, uid, ctx=None: uid,
    }
    _order = 'date desc'


class hse_safety_meeting_line(osv.osv):
    _name = 'hse.safety.meeting.line'
    _description = 'Safety meeting line'
    _columns = {
        'safety_meeting_id': fields.many2one('hse.safety.meeting', 'Safety meeting ID', required=True),
        'participant_id': fields.many2one('hr.employee', 'Participants', required=True),
    }


class hse_workplace_ispection(osv.osv):
    _name = 'hse.workplace.ispection'
    _description = 'Workplace ispection'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
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

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        if obj.name:
            return res
        my_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hse.workplace.ispection')])[0]
        conf_ids = self.pool.get('hse.code.config').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                     ('model_id', '=', my_id)])
        if conf_ids:
            num_name = self.pool.get('hse.code.config').browse(cr, uid, conf_ids)[0].name
            max_count = 0
            cr.execute('SELECT id FROM hse_workplace_ispection where project_id = %s and EXTRACT(YEAR FROM date) = %s ',
                       (obj.project_id.id, datetime.strptime(obj.date, '%Y-%m-%d').year))
            obj_ids = map(lambda x: x[0], cr.fetchall())
            for item in self.pool.get('hse.workplace.ispection').browse(cr, uid, obj_ids, context=context):
                s = item.name
                if s and int(s[len(num_name): len(s)]) > max_count:
                    max_count = int(s[len(num_name): len(s)])
            res[obj.id] = num_name + str(max_count + 1).zfill(4)
            return res
        return res

    _columns = {
        'date': fields.date('Date', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'name': fields.function(_set_name, type='char', string='Number', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('sent_mail', 'Sent to mail'), ('repaired', 'Repaired')],
                                  'State', readonly=True),
        'project_id': fields.many2one('project.project', 'Project', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'made_place': fields.char('Made place', size=200, required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}),

        'part': fields.selection([('a', 'A'), ('b', 'B'), ('c', 'C')], 'Part', required=True, readonly=True,
                                 states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department', required=True, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'captian_id': fields.many2one('hr.employee', 'Captians', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),

        'member_ids': fields.many2many('hr.employee', 'hse_workplace_ispection_mem_employee_rel', 'wo_is_id',
                                       'employee_id', 'Members', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'partner_ids': fields.many2many('hse.partner', 'hse_workplace_ispection_partner_rel', 'wo_is_id', 'partner_id',
                                        'Responsible partner', readonly=True, states={'draft': [('readonly', False)]}),
        'attachment_ids': fields.many2many('ir.attachment', 'hse_workplace_ispection_ir_attachments_rel', 'worplace_id',
                                           'attachment_id', 'Attachments', readonly=True,
                                           states={'draft': [('readonly', False), ]}),
        'cor_act_attach_ids': fields.many2many('ir.attachment', 'hse_workplace_ispection_cor_act_attach_rel',
                                               'worplace_id', 'attachment_id', 'Correct action image', readonly=True,
                                               states={'sent_mail': [('readonly', False), ]}),

        'wo_is_line': fields.one2many('hse.workplace.ispection.line', 'workplace_is_id', 'Workplace ispection lines',
                                      readonly=False, states={'repaired': [('readonly', True)]}),
        'good_job': fields.text('Good job', readonly=True, states={'draft': [('readonly', False)]}),
        'mail_line': fields.one2many('hse.workplace.ispection.mail.line', 'workplace_is_id', 'Mail line'),
        'mail_text': fields.text('Mail text'),
    }

    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(_('Error'), _('State is not draft'))
            else:
                return super(hse_workplace_ispection, self).unlink(cr, uid, ids, context)
        return True

    def get_mail_notice_workplace_ispection(self, cr, uid, context=None):
        '''Ажлын байрны үзлэг засагдаагүйг автоматаар мэдэгдэх'''
        worplace_id = self.pool.get('hse.workplace.ispection').search(cr, uid, [('state', '=', 'sent_mail')])
        for item in self.pool.get('hse.workplace.ispection').browse(cr, uid, worplace_id):
            self._get_mail(cr, uid, item.id, item, context=context)

        return True

    def _get_email_employee(self, cr, uid, ids, employee_id, user_mails, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        emp_mail = None
        if employee_id.work_email:
            if employee_id.work_email not in user_mails:
                emp_mail = employee_id.work_email
            else:
                return False
        else:
            if employee_id.parent_id.work_email and employee_id.parent_id.work_email not in user_mails:
                emp_mail = employee_id.parent_id.work_email
            else:
                return False
        return {'email': emp_mail}

    def send_emails(self, cr, uid, ids, subject, body, context=None):
        mail_mail = self.pool.get('mail.mail')
        obj = self.browse(cr, uid, ids, context)[0]
        mail_ids = []
        for item in obj.mail_line:
            mail_ids.append(mail_mail.create(cr, uid, {
                'email_from': self.pool.get('res.users').browse(cr, uid, uid).company_id.email,
                'email_to': item.mail,
                'subject': subject,
                'body_html': '%s' % body}, context=context))
        mail_mail.send(cr, uid, mail_ids, context=context)

    def _get_mail(self, cr, uid, ids, obj, context=None):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        action_id = \
        self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_workplace_ispection')[1]
        db_name = cr.dbname

        body = u'<p>Танд Ажлын Байрны Үзлэгээс <a href="' + unicode(base_url) + u'/web?db=' + unicode(
            db_name) + u'#id=' + str(obj.id) + u'&view_type=form&model=hse.workplace.ispection&action=' + str(
            action_id) + u'"> ' + unicode(obj.name) + u'</a> дугаартай хариу арга хэмжээ авах шаардлагатай дутагдал '
        if obj.state == 'sent_mail':
            body += u'ирлээ.</p>'
        if obj.state == 'repaired':
            body += u'засагдсан төлөвт орлоо.</p>'

        body += u'<table> <tr> <td>Хэлтэс</td><td style="font-weight: bold;">' + unicode(
            obj.department_id.name) + u'</td></tr><tr><td>Ээлж</td>'
        body += u'<td style="font-weight: bold;">' + unicode(obj.part.title()) + u'</td></tr><tr><td>Огноо</td>'
        body += u'<td style="font-weight: bold;">' + unicode(obj.date) + u'</td></tr><tr><td>Хийгдсэн газар</td>'
        body += u'<td style="font-weight: bold;">' + unicode(obj.made_place) + u'</td></tr><tr><td>Төсөл</td>'
        body += u'<td style="font-weight: bold;">' + unicode(obj.project_id.name) + u'</td></tr><tr><td>Дугаар</td>'
        body += u'<td style="font-weight: bold;">' + unicode(obj.name) + u'</td></tr></table>'

        body += u'<table cellspacing="1" border="1" cellpadding="4"><tr style="background-color: #4CAF50; color: white;">'
        body += u'<th>Аюулын зэрэг</th><th>Дутагдал ба аюул</th><th>Шаардлагатай хариу арга хэмжээ</th><th>Хариуцагч</th>'
        body += u'<th>Арга хэмжээ авах огноо</th><th>Авсан арга хэмжээ</th><th>Арга хэмжээ авсан ажилтан</th><th>Арга хэмжээ авсан огноо</th></tr>'
        for item in obj.wo_is_line:
            body += u'<tr><td>' + item.hazard_rating.title() + u'</td><td>' + item.failure_and_hazard + u'</td>'

            members_name = ''
            members = [x.id for x in item.employee_ids]
            for line in members:
                members_name += self.pool.get('hr.employee').browse(cr, uid, line).name + '<br/>'
            members = [x.id for x in item.partner_ids]
            for line in members:
                members_name += self.pool.get('hse.partner').browse(cr, uid, line).name + '<br/>'

            body += u'<td>' + item.required_corr_action + u'</td><td>' + members_name + u'</td><td>' + item.when_start + ' - ' + item.when_end + '</td>'
            if obj.state == 'repaired':
                body += u'<td>' + unicode(item.corrective_action_taken) + u'</td><td>' + unicode(
                    item.taken_employee_id.name) + '</td><td>' + unicode(item.repair_date) + '</td>'
            body += u'</tr>'
        body += u'</table>'
        mail_text = ''
        if obj.mail_text:
            mail_text = obj.mail_text
        self.send_emails(cr, uid, ids, u'Ажлын байрны үзлэг ' + unicode(obj.name),
                         unicode(body) + u'<br/>' + unicode(mail_text))
        sent_mail_users = ''
        for item in obj.mail_line:
            sent_mail_users += item.mail + '<br/>'

        message_post = u'Хариу арга хэмжээ авах'
        if obj.state == 'repaired':
            message_post = u'Засагдсан'

        self.pool.get('hse.workplace.ispection').message_post(cr, uid, [obj.id], body=unicode(
            message_post + u':<br/>Дараах хүмүүст майл илгээгдэв:<br/>' + sent_mail_users), type='notification',
                                                              subtype=None, parent_id=False, context=context)

        return True

    def mail_sent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if obj.state == 'draft':
            self.write(cr, uid, ids, {'state': 'sent_mail'})
        else:
            if obj.state == 'sent_mail':
                self.write(cr, uid, ids, {'state': 'repaired'})
                taken_employee_id = self.pool.get('hr.employee').browse(cr, uid,
                                                                        self.pool.get('hr.employee').search(cr, uid, [
                                                                            ('user_id', '=', uid)])).id
                self.pool.get('hse.workplace.ispection.line').write(cr, uid, self.pool.get(
                    'hse.workplace.ispection.line').search(cr, uid, [('workplace_is_id', '=', obj.id),
                                                                     ('is_repaired', '=', False)]),
                                                                    {'is_repaired': True,
                                                                     'repair_date': datetime.now().strftime('%Y-%m-%d'),
                                                                     'taken_employee_id': taken_employee_id})

        self._get_mail(cr, uid, ids, obj, context=context)

        return True

    def action_to_sent_mail(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        user_ids = []
        members = [x.id for x in obj.member_ids]
        if obj.wo_is_line:

            if not obj.mail_line:
                user_mails = []

                for item in members:
                    user_obj = self._get_email_employee(cr, uid, ids,
                                                        self.pool.get('hr.employee').browse(cr, uid, item), user_mails,
                                                        context)
                    if user_obj:
                        user_mails.append(user_obj['email'])
                user_obj = self._get_email_employee(cr, uid, ids, obj.captian_id, user_mails, context)
                if user_obj:
                    user_mails.append(user_obj['email'])

                for item in obj.wo_is_line:
                    members = [x.id for x in item.employee_ids]
                    for line in members:
                        user_obj = self._get_email_employee(cr, uid, ids,
                                                            self.pool.get('hr.employee').browse(cr, uid, line),
                                                            user_mails, context)
                        if user_obj:
                            user_mails.append(user_obj['email'])
                    members = [x.id for x in item.partner_ids]
                    for line in members:
                        if self.pool.get('hse.partner').browse(cr, uid, line).email not in user_mails:
                            user_mails.append(self.pool.get('hse.partner').browse(cr, uid, line).email)

                for item in user_mails:
                    data = {
                        'workplace_is_id': obj.id,
                        'mail': item,
                    }
                    line_id = self.pool.get('hse.workplace.ispection.mail.line').create(cr, uid, data, context=context)

            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.workplace.ispection'),
                                                                   ('name', '=', 'hse.workplace.ispection.mail.form')])
            return {
                'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'hse.workplace.ispection',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': obj.id,
                'context': context
            }
        else:
            raise osv.except_osv(_('Error'), _('Workplace ispection is empty'))

        return True

    def action_to_repaired(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.workplace.ispection'),
                                                               ('name', '=', 'hse.workplace.ispection.mail.form')])
        return {
            'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hse.workplace.ispection',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': obj.id,
            'context': context
        }

    def action_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    _defaults = {
        'date': fields.date.context_today,
        'state': 'draft',
    }
    _order = 'date desc'


class hse_workplace_ispection_mail_line(osv.osv):
    _name = 'hse.workplace.ispection.mail.line'
    _description = 'Mail line'
    _columns = {
        'workplace_is_id': fields.many2one('hse.workplace.ispection', 'Workplace ID', required=True,
                                           ondelete='cascade'),
        'mail': fields.char('Mail', required=True, size=100),
    }


class hse_workplace_ispection_line(osv.osv):
    _name = 'hse.workplace.ispection.line'
    _description = 'Workplace ispection line'

    def action_to_repaired(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if obj.corrective_action_taken:
            if len(self.pool.get('hse.workplace.ispection.line').search(cr, uid, [
                ('workplace_is_id', '=', obj.workplace_is_id.id), ('is_repaired', '=', False)])) == 1:
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.workplace.ispection'), (
                'name', '=', 'hse.workplace.ispection.mail.form')])
                return {
                    'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
                    'view_mode': 'form',
                    'view_id': view_id,
                    'view_type': 'form',
                    'res_model': 'hse.workplace.ispection',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'res_id': obj.workplace_is_id.id,
                    'context': context
                }
            else:
                taken_employee_id = self.pool.get('hr.employee').browse(cr, uid,
                                                                        self.pool.get('hr.employee').search(cr, uid, [
                                                                            ('user_id', '=', uid)])).id
                self.write(cr, uid, ids, {'is_repaired': True, 'repair_date': datetime.now().strftime('%Y-%m-%d'),
                                          'taken_employee_id': taken_employee_id})
        else:
            raise osv.except_osv(_('Error'), _('Corrective action taken is empty'))
        return True

    _columns = {
        'workplace_is_id': fields.many2one('hse.workplace.ispection', 'Workplace ID', required=True,
                                           ondelete='cascade'),
        'state': fields.related('workplace_is_id', 'state', type='char', string='State', readonly=True),
        'hazard_rating': fields.selection([('a', 'A'), ('b', 'B'), ('c', 'C')], 'Hazard rating', required=True,
                                          readonly=True, states={'draft': [('readonly', False)]}),
        'failure_and_hazard': fields.char('Failure and hazard', size=300, required=True, readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'required_corr_action': fields.char('Required corrective action', size=400, required=True, readonly=True,
                                            states={'draft': [('readonly', False)]}),
        'responsible': fields.reference('Responsible',
                                        selection=[('hr.employee', 'Employee'), ('hse.partner', 'Partner')]),
        'employee_ids': fields.many2many('hr.employee', 'hse_workplace_ispection_line_employee_rel', 'wo_is_id',
                                         'employee_id', 'Responsible employee', required=False, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'partner_ids': fields.many2many('hse.partner', 'hse_workplace_ispection_line_partner_rel', 'wo_is_id',
                                        'partner_id', 'Responsible partner', required=False, readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'when_start': fields.date('When start', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'when': fields.date('When', readonly=True, states={'draft': [('readonly', False)]}),
        'when_end': fields.date('When end', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'is_repaired': fields.boolean('Is repaired'),
        'corrective_action_taken': fields.char('Corrective action taken', size=200, readonly=True,
                                               states={'sent_mail': [('readonly', False)]}),
        'taken_employee_id': fields.many2one('hr.employee', 'Taken employee', readonly=True),
        'repair_date': fields.date('Repair date', readonly=True),
    }
    _defaults = {
        'state': 'draft',
        'is_repaired': False
    }


class hse_hazard_report(osv.osv):
    _name = 'hse.hazard.report'
    _description = 'Hazard report'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def create(self, cr, uid, vals, context=None):
        if vals['auto_number'] == True:
            obj_ids = self.pool.get('hse.hazard.report').search(cr, uid, [('project_id', '=', vals['project_id']), (
            'year', '=', datetime.strptime(vals['datetime'], '%Y-%m-%d %H:%M:%S').year), ('auto_number', '=', True)])
            max_count = 0
            for item in self.pool.get('hse.hazard.report').browse(cr, uid, obj_ids, context=context):
                s = item.name
                if s and int(s[1: len(s)]) > max_count:
                    max_count = int(s[1: len(s)])
            vals['name'] = 'H' + str(max_count + 1).zfill(5)
        result = super(hse_hazard_report, self).create(cr, uid, vals, context=context)
        return result

    def write(self, cr, uid, ids, vals, context=None):
        super(hse_hazard_report, self).write(cr, uid, ids, vals, context=context)

        vals = {}
        obj = self.browse(cr, uid, ids)
        if obj.auto_number and not obj.name:
            date_object = datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S')
            obj_ids = self.pool.get('hse.hazard.report').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                          ('year', '=', date_object.year),
                                                                          ('auto_number', '=', True),
                                                                          ('id', '!=', obj.id)])
            max_count = 0
            for item in self.pool.get('hse.hazard.report').browse(cr, uid, obj_ids, context=context):
                s = item.name
                if s and int(s[1: len(s)]) > max_count:
                    max_count = int(s[1: len(s)])
            vals['name'] = 'H' + str(max_count + 1).zfill(5)
        res = super(hse_hazard_report, self).write(cr, uid, ids, vals, context=context)

        return res

    _columns = {
        'datetime': fields.datetime('Datetime', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('sent_mail', 'Sent to mail'), ('repaired', 'Repaired')],
                                  'State', readonly=True),
        'auto_number': fields.boolean('Auto number', readonly=True, states={'draft': [('readonly', False)]}),
        'name': fields.char('Number', size=6, readonly=True, states={'draft': [('readonly', False)]}),
        'project_id': fields.many2one('project.project', 'Project', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'location_id': fields.many2one('hse.location', 'Location', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'hazard_type': fields.selection([('minor', 'Minor'), ('medium', 'Medium'), ('seriuos', 'Seriuos')],
                                        'Hazard type', required=True, readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'notify_emp_id': fields.reference('Notify employee',
                                          selection=[('hr.employee', 'Employee'), ('hse.partner', 'Partner')],
                                          required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'hazard_identification': fields.text('Hazard identification', required=True, readonly=True,
                                             states={'draft': [('readonly', False)]}),
        'corrective_action_to_be_taken': fields.text('Corrective action to be taken', required=True, readonly=True,
                                                     states={'draft': [('readonly', False)]}),
        'corrective_action_taken': fields.text('Corrective action taken', readonly=True,
                                               states={'sent_mail': [('readonly', False), ('required', True)]},
                                               required=False),
        'taken_datetime': fields.datetime('Taken dateime', readonly=True),
        'responsible': fields.reference('Responsible',
                                        selection=[('hr.employee', 'Employee'), ('hse.partner', 'Partner')],
                                        required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'mail_line': fields.one2many('hse.hazard.report.mail.line', 'hazard_id', 'Mail line'),
        'mail_text': fields.text('Mail text'),
        'taken_employee_id': fields.many2one('hr.employee', 'Taken employee', readonly=True),
    }

    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(_('Error'), _('State is not draft'))
            else:
                return super(hse_hazard_report, self).unlink(cr, uid, ids, context)
        return True

    def _get_email_employee(self, cr, uid, ids, employee_id, user_mails, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        emp_mail = False
        if 'hr.employee' in str(employee_id):
            if employee_id.work_email:
                if employee_id.work_email not in user_mails:
                    emp_mail = employee_id.work_email
            else:
                if employee_id.parent_id.work_email and employee_id.parent_id.work_email not in user_mails:
                    emp_mail = employee_id.parent_id.work_email

        else:
            if employee_id.email not in user_mails:
                emp_mail = employee_id.email
        if emp_mail:
            return {'email': emp_mail}
        return False

    def send_emails(self, cr, uid, ids, subject, body, context=None):
        mail_mail = self.pool.get('mail.mail')
        obj = self.browse(cr, uid, ids, context)[0]
        mail_ids = []
        for item in obj.mail_line:
            mail_ids.append(mail_mail.create(cr, uid, {
                'email_from': self.pool.get('res.users').browse(cr, uid, uid).company_id.email,
                'email_to': item.mail,
                'subject': subject,
                'body_html': '%s' % body}, context=context))
        mail_mail.send(cr, uid, mail_ids, context=context)
        return True

    def _get_mail(self, cr, uid, ids, obj, context=None):
        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_hazard_report')[1]
        db_name = cr.dbname
        trans_id = self.pool.get('ir.translation').search(cr, uid, [('module', '=', 'hse'), ('lang', '=', 'mn_MN'),
                                                                    ('src', '=', obj.hazard_type.title())],
                                                          limit=1)
        translation = self.pool.get('ir.translation').browse(cr, uid, trans_id)[0].value
        body = u'<p style="font-weight: bold;"> Дараах <a href="' + unicode(base_url) + u'/web?db=' + unicode(
            db_name) + u'#id=' + str(obj.id) + u'&view_type=form&model=hse.hazard.report&action=' + str(
            action_id) + u'">Аюулыг мэдээлэх хуудас ' + unicode(obj.name) + u'</a> '
        if obj.state == 'sent_mail':
            body += u'ирлээ.</p>'
        if obj.state == 'repaired':
            body += u'засагдсан төлөвт орлоо.</p>'

        date_time = datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S')
        timezone = pytz.timezone(self.pool.get('res.users').browse(cr, uid, uid).tz)
        date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)

        body += u'<table> <tr> <td>Огноо</td><td style="font-weight: bold;">' + str(
            date_time) + u'</td></tr><tr><td>Төсөл</td>'
        body += u'<td style="font-weight: bold;">' + unicode(
            obj.project_id.name) + u'</td></tr><tr><td>Аюулын төрөл</td>'
        body += u'<td style="font-weight: bold;">' + unicode(translation) + u'</td></tr><tr><td>Байрлал</td>'
        body += u'<td style="font-weight: bold;">' + obj.location_id.name + u'</td></tr><tr><td>Хариуцагч</td>'
        body += u'<td style="font-weight: bold;">' + obj.responsible.name + u'</td></tr><tr><td>Мэдээлсэн ажилтан</td>'
        body += u'<td style="font-weight: bold;">' + obj.notify_emp_id.name + u'</td></tr></table>'
        body += u'<table cellspacing="1" border="1" cellpadding="4"><tr style="background-color: #4CAF50; color: white;">'
        body += u'<th>Аюулын тодорхойлолт</th><th>Авах арга хэмжээ</th></tr><tr style="color: red;">'
        body += u'<td>' + obj.hazard_identification + '</td><td>' + obj.corrective_action_to_be_taken + '</td></tr></table>'

        if obj.state == 'repaired':
            body += u'<br/><span style="font-weight: bold;">Авагдсан арга хэмжээ: </span>  <span>' + obj.corrective_action_taken + '</span>'
            body += u'<br/><span style="font-weight: bold;">Арга хэмжээ авсан ажилтан: </span>  <span>' + obj.taken_employee_id.name + '</span>'
            body += u'<br/><span style="font-weight: bold;">Арга хэмжээ авсан огноо: </span>  <span>' + obj.taken_datetime + '</span>'
        mail_text = ''
        if obj.mail_text:
            mail_text = obj.mail_text
        self.send_emails(cr, uid, ids, u'Аюулыг мэдээлэх хуудас ' + unicode(obj.name),
                         body + u'<br/>' + unicode(mail_text), context=context)
        sent_mail_users = ''
        for item in obj.mail_line:
            sent_mail_users += item.mail + '<br/>'

        message_post = u'Хариу арга хэмжээ авах'
        if obj.state == 'repaired':
            message_post = u'Засагдсан'

        self.pool.get('hse.hazard.report').message_post(cr, uid, [obj.id], body=unicode(
            message_post + u':<br/>Дараах хүмүүст майл илгээгдэв:<br/>' + sent_mail_users), type='notification',
                                                        subtype=None, parent_id=False, context=context)

        return True

    def mail_sent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if obj.state == 'draft':
            self.write(cr, uid, ids, {'state': 'sent_mail'})
        else:
            if obj.state == 'sent_mail':
                taken_employee_id = self.pool.get('hr.employee').browse(cr, uid,
                                                                        self.pool.get('hr.employee').search(cr, uid, [
                                                                            ('user_id', '=', uid)])).id
                self.write(cr, uid, ids,
                           {'state': 'repaired', 'taken_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'taken_employee_id': taken_employee_id})

        self._get_mail(cr, uid, ids, obj, context=context)
        return True

    def action_to_sent_mail(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        user_mails = []
        if not obj.mail_line:
            user_obj = self._get_email_employee(cr, uid, ids, obj.responsible, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])
            user_obj = self._get_email_employee(cr, uid, ids, obj.notify_emp_id, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])
            for item in user_mails:
                data = {
                    'hazard_id': obj.id,
                    'mail': item,
                }
                line_id = self.pool.get('hse.hazard.report.mail.line').create(cr, uid, data, context=context)
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.hazard.report'),
                                                               ('name', '=', 'hse.hazard.report.mail.form')])
        return {
            'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hse.hazard.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': obj.id,
            'context': context
        }

    def action_to_repaired(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.hazard.report'),
                                                               ('name', '=', 'hse.hazard.report.mail.form')])
        return {
            'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hse.hazard.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': obj.id,
            'context': context
        }

    def action_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def get_mail_notice_hazard_report(self, cr, uid, context=None):
        '''Аюулыг мэдээлэх хуудас засагдаагүйг автоматаар мэдэгдэх'''
        hazard_ids = self.pool.get('hse.hazard.report').search(cr, uid, [('state', '=', 'sent_mail')])
        for item in self.pool.get('hse.hazard.report').browse(cr, uid, hazard_ids):
            self._get_mail(cr, uid, item.id, item, context=context)

        return True

    _defaults = {
        'datetime': fields.date.context_today,
        'state': 'draft',
        'auto_number': True
    }
    _order = 'datetime desc'


class hse_hazard_report_mail_line(osv.osv):
    _name = 'hse.hazard.report.mail.line'
    _description = 'Mail line'
    _columns = {
        'hazard_id': fields.many2one('hse.hazard.report', 'Hazard ID', required=True, ondelete='cascade'),
        'mail': fields.char('Mail', required=True, size=100),
    }


class hse_risk_assessment(osv.osv):
    _name = 'hse.risk.assessment'
    _description = 'Risk assessment'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        if obj.name:
            return res
        my_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hse.risk.assessment')])[0]
        conf_ids = self.pool.get('hse.code.config').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                     ('model_id', '=', my_id)])
        if conf_ids:
            num_name = self.pool.get('hse.code.config').browse(cr, uid, conf_ids)[0].name
            max_count = 0
            cr.execute('SELECT id FROM hse_risk_assessment where project_id = %s and EXTRACT(YEAR FROM datetime) = %s ',
                       (obj.project_id.id, datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S').year))
            obj_ids = map(lambda x: x[0], cr.fetchall())
            for item in self.pool.get('hse.risk.assessment').browse(cr, uid, obj_ids, context=context):
                s = item.name
                if s and int(s[len(num_name): len(s)]) > max_count:
                    max_count = int(s[len(num_name): len(s)])
            res[obj.id] = num_name + str(max_count + 1).zfill(4)
            return res
        return res

    _columns = {
        'datetime': fields.datetime('Datetime', required=True, states={'done': [('readonly', True)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('done', 'Done')], 'State', readonly=True,
                                  track_visibility='onchange'),
        'name': fields.function(_set_name, type='char', string='Number', readonly=True, store=True),
        'project_id': fields.many2one('project.project', 'Project', required=True,
                                      states={'done': [('readonly', True)]}),
        'location_id': fields.many2one('hse.location', 'Location', required=True,
                                       states={'done': [('readonly', True)]}),
        'made_work': fields.char('Made Work', required=True, size=200, states={'done': [('readonly', True)]}),
        'monitoring_user_id': fields.many2one('hr.employee', 'Monitoring user', required=True,
                                              states={'done': [('readonly', True)]}),
        'captian_user_id': fields.many2one('hr.employee', 'Captian', required=True,
                                           states={'done': [('readonly', True)]}),
        'member_ids': fields.many2many('hr.employee', 'hse_risk_assessment_mem_employee_rel', 'wo_is_id', 'employee_id',
                                       'Members', states={'done': [('readonly', True)]}),
        'risk_assessment_table': fields.one2many('hse.risk.assessment.table', 'risk_assessment_id',
                                                 'Workplace ispection lines', states={'done': [('readonly', True)]}),
        'attachment_ids': fields.many2many('ir.attachment', 'hse_risk_assessment_ir_attachments_rel', 'assessment_id',
                                           'attachment_id', 'Attachments', readonly=True,
                                           states={'draft': [('readonly', False)]}),
    }

    def action_to_done(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    _defaults = {
        'datetime': fields.date.context_today,
        'state': 'draft',
    }
    _order = 'datetime desc'


class hse_risk_assessment_table(osv.osv):
    _name = 'hse.risk.assessment.table'
    _description = 'Risk assessment table'
    _columns = {
        'risk_assessment_id': fields.many2one('hse.risk.assessment', 'Assessment ID', required=True),
        'step': fields.integer('Step'),
        'task_steps': fields.text('Task steps', required=True),
        'potential_hazard': fields.text('Potential hazard', required=True),
        'risk_rating_id': fields.many2one('hse.risk.rating', 'Risk rating', required=True),
        'controls_to_reduce_risk': fields.text('Controls to reduce risk', required=True),
        'reduced_risk_rating_id': fields.many2one('hse.risk.rating', 'Reduced risk rating', required=True),
        'employee_ids': fields.many2many('hr.employee', 'hse_workplace_ispection_line_employee_rel', 'wo_is_id',
                                         'employee_id', 'Responsible employee'),
        'partner_ids': fields.many2many('hse.partner', 'hse_workplace_ispection_line_partner_rel', 'wo_is_id',
                                        'partner_id', 'Responsible partner'),

        # 'responsible': fields.many2one('hr.employee','Responsible', required=True),
    }
    _order = 'step asc'


class hse_injury_entry(osv.osv):
    _name = 'hse.injury.entry'
    _description = 'Injury entry'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
    def _set_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        date_object = datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S')
        res[obj.id] = {
            'year': date_object.year,
            'month': date_object.month,
            'day': date_object.day
        }
        return res

    def write(self, cr, uid, ids, vals, context=None):
        super(hse_injury_entry, self).write(cr, uid, ids, vals, context)
        obj = self.browse(cr, uid, ids, context)[0]

        if 'datetime' in vals or 'project_id' in vals or 'accident_type' in vals:
            vals = {}
            obj = self.browse(cr, uid, ids)[0]
            my_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hse.injury.entry')])[0]
            conf_ids = self.pool.get('hse.code.config').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                         ('model_id', '=', my_id)])
            if conf_ids:
                num_name = self.pool.get('hse.code.config').browse(cr, uid, conf_ids)[0].name
                if obj.accident_type.value == 'FIRST_AID':
                    num_name += u'АТУ-'
                elif obj.accident_type.value == 'SPILL':
                    num_name += u'АСГ-'
                elif obj.accident_type.value == 'FIRE':
                    num_name += u'ГАЛ-'
                elif obj.accident_type.value == 'NEAR_MISS_INCIDENT':
                    num_name += u'ОДТ-'
                elif obj.accident_type.value == 'MEDICAL_AID':
                    num_name += u'ЭТУ-'
                elif obj.accident_type.value == 'PROPERTY_DAMAGE':
                    num_name += u'ӨМЧ-'
                max_count = 0
                # cr.execute('SELECT id FROM hse_injury_entry where id!=%s and project_id = %s and year= %s and accident_type=%s',(obj.id, obj.project_id.id, obj.year, obj.accident_type.id))
                obj_ids = self.pool.get('hse.injury.entry').search(cr, uid, [('id', '!=', obj.id),
                                                                             ('project_id', '=', obj.project_id.id),
                                                                             ('year', '=', obj.year), (
                                                                             'accident_type', '=',
                                                                             obj.accident_type.id)])
                for item in self.pool.get('hse.injury.entry').browse(cr, uid, obj_ids, context=context):
                    s = item.name
                    if s and int(s[len(num_name): len(s)]) > max_count:
                        max_count = int(s[len(num_name): len(s)])
                vals['name'] = num_name + str(max_count + 1).zfill(4)
                super(hse_injury_entry, self).write(cr, uid, ids, vals, context)
        return True

    _columns = {
        'datetime': fields.datetime('Datetime', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'state': fields.selection([('draft', 'Draft'), ('sent_mail', 'Sent to mail'), ('closed', 'Closed'),
                                   ('cor_act_closed', 'Corrective actions closed')], 'State', readonly=True),
        'name': fields.char('Number', size=20, readonly=True, states={'draft': [('readonly', False)]}),
        'accident_name': fields.char('Accident name', size=200, required=True),
        'technic_ids': fields.many2many('technic', 'hse_injury_entry_technic_rel', 'injury_id', 'technic_id',
                                        'Technic'),
        # 'accident_name': fields.char('Accident name', size=100, required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'lost_day': fields.integer('Lost day'),
        'involved_employee': fields.many2many('hr.employee', 'hse_injury_entry_involved_employee_rel', 'injury_id',
                                              'employee_id', 'Involved employee'),
        # 'lost_day': fields.integer('Lost day', readonly=True, states={'cor_act_closed':[('readonly',False)]}),
        'project_id': fields.many2one('project.project', 'Project', required=True, readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'department_id': fields.many2one('hr.department', 'Department', required=True, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'project_manager_id': fields.many2one('hr.employee', 'Project manager', required=True, readonly=True,
                                              states={'draft': [('readonly', False)]}),
        'dep_manager_id': fields.many2one('hr.employee', 'Department manager', readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'general_master_id': fields.many2one('hr.employee', 'General master', readonly=True,
                                             states={'draft': [('readonly', False)]}),
        'master_id': fields.many2one('hr.employee', 'Master', readonly=True, states={'draft': [('readonly', False)]}),

        'accident_type': fields.many2one('hse.accident.type', 'Accident type', required=True, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'value': fields.related('accident_type', 'value', type='char', relation='hse.accident.cause', store=True,
                                string='Value'),

        'location_accident': fields.char('The location of the accident', size=100, required=True, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'consequence_id': fields.many2one('hse.consequence', 'Potential significance', required=True, readonly=True,
                                          states={'draft': [('readonly', False)]}),
        'likelihood_id': fields.many2one('hse.likelihood', 'Likelihood reoccure', required=True, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'before_injury': fields.text('Before injury', required=True, readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'how_do_injury': fields.text('How do injury', required=True, readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'next_injury': fields.text('Next injury', required=True, readonly=True,
                                   states={'draft': [('readonly', False)]}),
        'is_lti': fields.boolean('Is LTI', readonly=True, states={'draft': [('readonly', False)]}),
        'accident_line': fields.one2many('hse.injury.accident.line', 'injury_id', 'Accident line', readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'corrective_action_line': fields.one2many('hse.injury.corrective.action.line', 'injury_id',
                                                  'Corrective action line', readonly=False,
                                                  states={'cor_act_closed': [('readonly', True)]}),
        'audit_line': fields.one2many('hse.injury.audit.line', 'injury_id', 'Audit line', readonly=True,
                                      states={'draft': [('readonly', False)]}),
        'audit_conclusion_line': fields.one2many('hse.injury.audit.conclusion.line', 'injury_id',
                                                 'Audit conclusion line', readonly=False,
                                                 states={'cor_act_closed': [('readonly', True)]}),
        'factor_line': fields.one2many('hse.injury.factor.line', 'injury_id', 'Factor line', readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'attachment_ids': fields.many2many('ir.attachment', 'hse_injury_entry_ir_attachments_rel', 'injury_id',
                                           'attachment_id', 'Attachments', readonly=True,
                                           states={'draft': [('readonly', False)]}),
        'cor_act_attach_ids': fields.many2many('ir.attachment', 'hse_injury_entry_cor_act_attach_rel', 'injury_id',
                                               'attachment_id', 'Correct action image', readonly=True,
                                               states={'closed': [('readonly', False), ]}),
        'desc_attach_ids': fields.many2many('ir.attachment', 'hse_injury_entry_desc_attach_rel', 'injury_id',
                                            'attachment_id', 'Description image', readonly=True,
                                            states={'draft': [('readonly', False), ]}),
        'mail_line': fields.one2many('hse.injury.entry.mail.line', 'injury_id', 'Mail line'),
        'mail_text': fields.text('Mail text'),
    }

    def create(self, cr, uid, vals, context=None):
        ids = super(hse_injury_entry, self).create(cr, uid, vals, context=context)
        obj = self.browse(cr, uid, ids, context)[0]
        res = {}
        if 'project_id' in vals or 'accident_type' in vals:
            obj = self.browse(cr, uid, ids)[0]
            my_id = self.pool.get('ir.model').search(cr, uid, [('model', '=', 'hse.injury.entry')])[0]
            conf_ids = self.pool.get('hse.code.config').search(cr, uid, [('project_id', '=', obj.project_id.id),
                                                                         ('model_id', '=', my_id)])
            if conf_ids:
                num_name = self.pool.get('hse.code.config').browse(cr, uid, conf_ids)[0].name
                if obj.accident_type.value == 'FIRST_AID':
                    num_name += u'АТУ-'
                elif obj.accident_type.value == 'SPILL':
                    num_name += u'АСГ-'
                elif obj.accident_type.value == 'FIRE':
                    num_name += u'ГАЛ-'
                elif obj.accident_type.value == 'NEAR_MISS_INCIDENT':
                    num_name += u'ОДТ-'
                elif obj.accident_type.value == 'MEDICAL_AID':
                    num_name += u'ЭТУ-'
                elif obj.accident_type.value == 'PROPERTY_DAMAGE':
                    num_name += u'ӨМЧ-'
                max_count = 0
                cr.execute(
                    'SELECT id FROM hse_injury_entry where project_id = %s and EXTRACT(YEAR FROM datetime) = %s and accident_type=%s',
                    (
                    obj.project_id.id, datetime.strptime(obj.datetime, '%Y-%m-%d %H:%M:%S').year, obj.accident_type.id))
                obj_ids = map(lambda x: x[0], cr.fetchall())
                for item in self.pool.get('hse.injury.entry').browse(cr, uid, obj_ids, context=context):
                    s = item.name
                    if s and int(s[len(num_name): len(s)]) > max_count:
                        max_count = int(s[len(num_name): len(s)])
                res['name'] = num_name + str(max_count + 1).zfill(4)
                super(hse_injury_entry, self).write(cr, uid, ids, res, context)

        return ids

    def unlink(self, cr, uid, ids, context=None):
        for item in self.browse(cr, uid, ids):
            if item.state != 'draft':
                raise osv.except_osv(_('Error'), _('State is not draft'))
            else:
                return super(hse_injury_entry, self).unlink(cr, uid, ids, context)
        return True

    def _get_email_employee(self, cr, uid, ids, employee_id, user_mails, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        emp_mail = None
        if employee_id.work_email:
            if employee_id.work_email not in user_mails:
                emp_mail = employee_id.work_email
            else:
                return False
        else:
            if employee_id.parent_id.work_email and employee_id.parent_id.work_email not in user_mails:
                emp_mail = employee_id.parent_id.work_email
            else:
                return False
        return {'email': emp_mail}

    def send_emails(self, cr, uid, ids, subject, body, context=None):
        mail_mail = self.pool.get('mail.mail')
        obj = self.browse(cr, uid, ids, context)[0]
        mail_ids = []
        for item in obj.mail_line:
            mail_ids.append(mail_mail.create(cr, uid, {
                'email_from': self.pool.get('res.users').browse(cr, uid, uid).company_id.email,
                'email_to': item.mail,
                'subject': subject,
                'body_html': '%s' % body}, context=context))
        mail_mail.send(cr, uid, mail_ids, context=context)

    def mail_sent(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if obj.state == 'draft':
            self.write(cr, uid, ids, {'state': 'sent_mail'})
        elif obj.state == 'sent_mail':
            self.write(cr, uid, ids, {'state': 'closed'})
        elif obj.state == 'closed':
            self.write(cr, uid, ids, {'state': 'cor_act_closed'})
            taken_employee_id = self.pool.get('hr.employee').browse(cr, uid,
                                                                    self.pool.get('hr.employee').search(cr, uid, [
                                                                        ('user_id', '=', uid)])).id
            self.pool.get('hse.injury.corrective.action.line').write(cr, uid, self.pool.get(
                'hse.injury.corrective.action.line').search(cr, uid,
                                                            [('injury_id', '=', obj.id), ('is_taken', '=', False)]),
                                                                     {'is_taken': True,
                                                                      'taken_date': datetime.now().strftime('%Y-%m-%d'),
                                                                      'taken_employee_id': taken_employee_id})

        base_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
        action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_injury_entry')[1]
        db_name = request.session.db

        subject = ''
        body = u'Дараах <a href="' + unicode(base_url) + u'/web?db=' + unicode(db_name) + u'#id=' + str(
            obj.id) + u'&view_type=form&model=hse.injury.entry&action=' + str(
            action_id) + u'">Осол тохиолдол ' + unicode(obj.name) + u'</a> '

        if obj.state == 'sent_mail':
            subject = u' ДҮГНЭЛТ бичнэ үү'
        elif obj.state == 'closed':
            body += u'хариу арга хэмжээ авна уу'
            body += u'<table cellspacing="1" border="1" cellpadding="4"><tr style="background-color: #4CAF50; color: white;">'
            body += u'<th>Хариу арга хэмжээ юуг?</th><th>Хэн?</th><th>Хэрхэн яаж?</th><th>Хэзээ?</th>'
            body += u'<th>Авагдсан арга хэмжээ</th><th>Арга хэмжээ авсан огноо</th></tr>'
            for item in obj.corrective_action_line:
                members_name = ''
                members = [x.id for x in item.employee_ids]
                for line in members:
                    members_name += self.pool.get('hr.employee').browse(cr, uid, line).name + '<br/>'
                members = [x.id for x in item.partner_ids]
                for line in members:
                    members_name += self.pool.get('hse.partner').browse(cr, uid, line).name + '<br/>'

                body += u'<tr><td>' + item.corrective_action_what + u'</td><td>' + members_name + u'</td>'
                body += u'<td>' + item.how + u'</td><td>' + item.when_start + ' - ' + item.when_end + '</td>'
                body += u'</tr>'
            body += u'</table>'

            subject = u' хариу арга хэмжээ авна уу'
        elif obj.state == 'cor_act_closed':
            body += u'хариу арга хэмжээ авагдлаа'
            body += u'<table cellspacing="1" border="1" cellpadding="4"><tr style="background-color: #4CAF50; color: white;">'
            body += u'<th>Хариу арга хэмжээ юуг?</th><th>Хэн?</th><th>Хэрхэн яаж?</th><th>Хэзээ?</th>'
            body += u'<th>Авагдсан арга хэмжээ</th><th>Арга хэмжээ авсан ажилтан</th><th>Арга хэмжээ авсан огноо</th></tr>'
            for item in obj.corrective_action_line:
                members_name = ''
                members = [x.id for x in item.employee_ids]
                for line in members:
                    members_name += self.pool.get('hr.employee').browse(cr, uid, line).name + '<br/>'
                members = [x.id for x in item.partner_ids]
                for line in members:
                    members_name += self.pool.get('hse.partner').browse(cr, uid, line).name + '<br/>'
                body += u'<tr><td>' + item.corrective_action_what + u'</td><td>' + members_name + u'</td>'
                body += u'<td>' + item.how + u'</td><td>' + item.when_start + ' - ' + item.when_end + '</td>'
                body += u'<td>' + unicode(item.corrective_action_taken) + u'</td><td>' + unicode(
                    item.taken_employee_id.name) + '</td><td>' + unicode(item.taken_date) + '</td>'
                body += u'</tr>'
            body += u'</table>'
            subject = u' хариу арга хэмжээ авагдлаа'

        mail_text = ''
        if obj.mail_text:
            mail_text = obj.mail_text
        self.send_emails(cr, uid, ids, u'Осол тохиолдол ' + unicode(obj.name) + subject,
                         body + u'<br/>' + unicode(mail_text))
        sent_mail_users = ''
        for item in obj.mail_line:
            sent_mail_users += item.mail + '<br/>'

        message_post = u'Дугнэлт бичих'
        if obj.state == 'sent_mail':
            message_post = u'Дугнэлт бичих'
        elif obj.state == 'closed':
            message_post = u'Хариу арга хэмжээ авах'
        elif obj.state == 'cor_act_closed':
            message_post = u'Хариу арга хэмжээ авагдсан'

        self.pool.get('hse.injury.entry').message_post(cr, uid, [obj.id], body=unicode(
            message_post + u':<br/>Дараах хүмүүст майл илгээгдэв:<br/>' + sent_mail_users), type='notification',
                                                       subtype=None, parent_id=False, context=context)

        return True

    def action_to_cor_act_closed(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.injury.entry'),
                                                               ('name', '=', 'hse.injury.entry.mail.form')])
        return {
            'name': _("Дараах хүмүүст майл илгээж мэдэгдэх"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hse.injury.entry',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': obj.id,
            'context': context
        }

    def action_to_sent_mail(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        user_mails = []
        if not obj.mail_line:
            if obj.audit_conclusion_line:
                for item in obj.audit_conclusion_line:
                    user_obj = self._get_email_employee(cr, uid, ids, item.employee_id, user_mails, context)
                    if user_obj:
                        user_mails.append(user_obj['email'])
            else:
                raise osv.except_osv(_('Error'), _('Injury audit conclusion line is empty'))

            if obj.audit_line:
                for item in obj.audit_line:
                    user_obj = self._get_email_employee(cr, uid, ids, item.employee_id, user_mails, context)
                    if user_obj:
                        user_mails.append(user_obj['email'])
            else:
                raise osv.except_osv(_('Error'), _('Injury audit line is empty'))

            for item in user_mails:
                data = {
                    'injury_id': obj.id,
                    'mail': item,
                }
                line_id = self.pool.get('hse.injury.entry.mail.line').create(cr, uid, data, context=context)

        view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.injury.entry'),
                                                               ('name', '=', 'hse.injury.entry.mail.form')])
        return {
            'name': _("Дүгнэлт бичих дараах хүмүүст майл илгээж мэдэгдэх"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'hse.injury.entry',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': obj.id,
            'context': context
        }

    def action_to_closed(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        user_mails = []
        if obj.corrective_action_line:
            for item in obj.audit_conclusion_line:
                if not item.conclusion or not item.date:
                    raise osv.except_osv(_('Error'), _('Conclusion is empty'))

            for item in obj.corrective_action_line:
                members = [x.id for x in item.employee_ids]
                for line in members:
                    user_obj = self._get_email_employee(cr, uid, ids,
                                                        self.pool.get('hr.employee').browse(cr, uid, line), user_mails,
                                                        context)
                    if user_obj:
                        user_mails.append(user_obj['email'])
                members = [x.id for x in item.partner_ids]
                for line in members:
                    if self.pool.get('hse.partner').browse(cr, uid, line).email not in user_mails:
                        user_mails.append(self.pool.get('hse.partner').browse(cr, uid, line).email)

            emp_obj = self.pool.get('hr.employee').browse(cr, uid, self.pool.get('hr.employee').search(cr, uid, [
                ('user_id', '=', obj.project_manager_id.id)]))
            user_obj = self._get_email_employee(cr, uid, ids, emp_obj, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])

            user_obj = self._get_email_employee(cr, uid, ids, obj.general_master_id, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])

            user_obj = self._get_email_employee(cr, uid, ids, obj.master_id, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])

            user_obj = self._get_email_employee(cr, uid, ids, obj.dep_manager_id, user_mails, context)
            if user_obj:
                user_mails.append(user_obj['email'])

            for item in user_mails:
                data = {
                    'injury_id': obj.id,
                    'mail': item,
                }
                self.pool.get('hse.injury.entry.mail.line').create(cr, uid, data, context=context)
            view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.injury.entry'),
                                                                   ('name', '=', 'hse.injury.entry.mail.form')])

            return {
                'name': _("Хариу арга хэмжээ авах дараах хүмүүст майл илгээж мэдэгдэх"),
                'view_mode': 'form',
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'hse.injury.entry',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': obj.id,
                'context': context
            }
        else:
            raise osv.except_osv(_('Error'), _('Injury corrective action line is empty'))

        return True

    def action_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'})
        return True

    def import_cause(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]

        if obj.accident_line:
            return {}
        cause_ids = self.pool.get('hse.accident.cause').search(cr, uid, [])

        for item in cause_ids:
            data = {'injury_id': obj.id,
                    'accident_cause_id': item,
                    'type': self.pool.get('hse.accident.factor').browse(cr, uid, [
                        self.pool.get('hse.accident.cause').browse(cr, uid, item).factor_id.id]).type
                    }
            line_id = self.pool.get('hse.injury.accident.line').create(cr, uid, data, context=context)
        line_ids = self.pool.get('hse.injury.accident.line').search(cr, uid, [('injury_id', '=', obj.id)])
        return {
            'value': {
                'accident_line': line_ids
            }
        }

    _defaults = {
        'datetime': fields.date.context_today,
        'state': 'draft',
    }
    _order = 'datetime desc, name asc'


class hse_injury_entry_mail_line(osv.osv):
    _name = 'hse.injury.entry.mail.line'
    _description = 'Mail line'
    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Injury ID', required=True, ondelete='cascade'),
        'mail': fields.char('Mail', required=True, size=100),
    }


class hse_injury_accident_line(osv.osv):
    _name = 'hse.injury.accident.line'
    _description = 'Injury accident line'

    def write(self, cr, uid, ids, vals, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if 'check' in vals:
            factor_ids = self.pool.get('hse.injury.factor.line').search(cr, uid, [('injury_id', '=', obj.injury_id.id),
                                                                                  ('factor_id', '=', obj.factor_id.id)])
            if not obj.check:
                if not factor_ids:
                    data = {
                        'injury_id': obj.injury_id.id,
                        'factor_id': obj.factor_id.id,
                        'notes': obj.accident_cause_id.name
                    }
                    self.pool.get('hse.injury.factor.line').create(cr, uid, data, context=context)
                else:
                    note = obj.accident_cause_id.name + '\n'
                    for item in self.browse(cr, uid, self.search(cr, uid, [('injury_id', '=', obj.injury_id.id),
                                                                           ('factor_id', '=', obj.factor_id.id),
                                                                           ('check', '=', True)])):
                        note += item.accident_cause_id.name + '\n'
                    self.pool.get('hse.injury.factor.line').write(cr, uid, factor_ids, {'notes': note}, context=context)
            else:
                lines_ids = self.search(cr, uid,
                                        [('injury_id', '=', obj.injury_id.id), ('factor_id', '=', obj.factor_id.id),
                                         ('check', '=', True), ('id', '!=', obj.id)])
                if lines_ids:
                    note = ''
                    for item in self.browse(cr, uid, self.search(cr, uid, [('injury_id', '=', obj.injury_id.id),
                                                                           ('factor_id', '=', obj.factor_id.id),
                                                                           ('check', '=', True),
                                                                           ('id', '!=', obj.id)])):
                        note += item.accident_cause_id.name + '\n'
                    self.pool.get('hse.injury.factor.line').write(cr, uid, factor_ids, {'notes': note}, context=context)
                else:
                    self.pool.get('hse.injury.factor.line').unlink(cr, uid, factor_ids, context=context)

        return super(hse_injury_accident_line, self).write(cr, uid, ids, vals, context)

    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Accident ID', required=True, ondelete='cascade'),
        'accident_cause_id': fields.many2one('hse.accident.cause', 'Accident cause', required=True),
        'sequence': fields.related('accident_cause_id', 'sequence', type='integer', string='Sequence',
                                   relation='hse.accident.cause', store=True, readonly=True),
        'factor_id': fields.related('accident_cause_id', 'factor_id', type='many2one', string='Factor',
                                    relation='hse.accident.factor', store=True, readonly=True),
        'state': fields.related('injury_id', 'state', type='char', string='State', relation='hse.injury.entry'),
        'type': fields.char('Type', size=50),
        'check': fields.boolean('Check'),
    }
    _order = 'sequence asc'


class hse_injury_factor_line(osv.osv):
    _name = 'hse.injury.factor.line'
    _description = 'Injury factor line'

    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Accident ID', required=True, ondelete='cascade'),
        'notes': fields.text('Notes'),
        'factor_id': fields.many2one('hse.accident.factor', 'Factor'),
        'state': fields.related('injury_id', 'state', type='char', string='State', relation='hse.injury.entry'),
        'type': fields.related('factor_id', 'type', type='char', string='Type', relation='hse.accident.factor',
                               readonly=True),
    }


class hse_injury_corrective_action_line(osv.osv):
    _name = 'hse.injury.corrective.action.line'
    _description = 'Injury corrective action line'

    def action_to_taken(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids, context)[0]
        if obj.corrective_action_taken:
            if len(self.pool.get('hse.injury.corrective.action.line').search(cr, uid,
                                                                             [('injury_id', '=', obj.injury_id.id),
                                                                              ('is_taken', '=', False)])) == 1:
                view_id = self.pool.get('ir.ui.view').search(cr, uid, [('model', '=', 'hse.injury.entry'),
                                                                       ('name', '=', 'hse.injury.entry.mail.form')])
                return {
                    'name': _("Хариу арга хэмжээ авагдлаа дараах хүмүүст майл илгээж мэдэгдэх"),
                    'view_mode': 'form',
                    'view_id': view_id,
                    'view_type': 'form',
                    'res_model': 'hse.injury.entry',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'res_id': obj.injury_id.id,
                    'context': context
                }
            else:
                taken_employee_id = self.pool.get('hr.employee').browse(cr, uid,
                                                                        self.pool.get('hr.employee').search(cr, uid, [
                                                                            ('user_id', '=', uid)])).id
                self.write(cr, uid, ids, {'is_taken': True, 'taken_date': datetime.now().strftime('%Y-%m-%d'),
                                          'taken_employee_id': taken_employee_id})
        else:
            raise osv.except_osv(_('Error'), _('Corrective action taken is empty'))
        return True

    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Accident ID', required=True, ondelete='cascade'),
        'state': fields.related('injury_id', 'state', type='char', string='State', readonly=True),
        'corrective_action_what': fields.char('Corrective action what?', size=350, required=True, readonly=True,
                                              states={'draft': [('readonly', False)]}),
        'who': fields.many2one('hr.employee', string='Who?', readonly=True, states={'draft': [('readonly', False)]}),
        'employee_ids': fields.many2many('hr.employee', 'hse_injury_corrective_action_line_employee_rel', 'injury_id',
                                         'employee_id', 'Who employee', required=False, readonly=True,
                                         states={'draft': [('readonly', False)]}),
        'partner_ids': fields.many2many('hse.partner', 'hse_injury_corrective_action_line_partner_rel', 'injury_id',
                                        'partner_id', 'Who partner', required=False, readonly=True,
                                        states={'draft': [('readonly', False)]}),
        'how': fields.char('How?', size=300, required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'when_start': fields.date('When start?', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'when': fields.date('When start?', readonly=True, states={'draft': [('readonly', False)]}),
        'when_end': fields.date('When end?', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'is_taken': fields.boolean('Is taken', readonly=True),
        'corrective_action_taken': fields.text('Corrective action taken', readonly=True,
                                               states={'closed': [('readonly', False)]}),
        'taken_employee_id': fields.many2one('hr.employee', 'Taken employee', readonly=True),
        'taken_date': fields.date('Taken date', readonly=True),
    }
    _defaults = {
        'state': 'draft',
    }


class hse_injury_audit_line(osv.osv):
    _name = 'hse.injury.audit.line'
    _description = 'Injury audit line'
    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Accident ID', required=True, ondelete='cascade'),
        'employee_id': fields.many2one('hr.employee', 'Name', required=True),
        'job_id': fields.related('employee_id', 'job_id', type='many2one', string='Job', relation='hr.job', store=True,
                                 readonly=True),
    }


class hse_injury_audit_conclusion_line(osv.osv):
    _name = 'hse.injury.audit.conclusion.line'
    _description = 'Injury audit conclusion line'
    _columns = {
        'injury_id': fields.many2one('hse.injury.entry', 'Accident ID', required=True, ondelete='cascade'),
        'state': fields.related('injury_id', 'state', type='char', string='State', readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Name', required=True, readonly=True,
                                       states={'draft': [('readonly', False)]}),
        'job_id': fields.related('employee_id', 'job_id', type='many2one', string='Job', relation='hr.job', store=True,
                                 readonly=True),
        'conclusion': fields.text('Conclusion', readonly=True, states={'sent_mail': [('readonly', False)]}),
        'date': fields.date('Date', readonly=True, states={'sent_mail': [('readonly', False)]}),
    }
    _defaults = {
        'state': 'draft',
    }


class hse_rules_documents_description(osv.osv):
    _name = 'hse.rules.documents.description'

    _columns = {
        'description_id': fields.many2one('hse.rules.documents', 'Document'),
        'description': fields.char('Description', required=True),
    }


class hse_rules_documents_name(osv.osv):
    _name = 'hse.rules.documents.name'

    _columns = {
        'name_id': fields.one2many('hse.rules.documents', 'name_id', 'Name'),
        'name': fields.char('Name', required=True),
    }


class hse_rules_documents(osv.osv):
    _name = 'hse.rules.documents'
    _description = 'Rules documents'
    _inherit = ["mail.thread"]

    # by Bayasaa Өдөрөөр салгах
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

    _columns = {
        'date': fields.date('Date', required=True),
        'year': fields.function(_set_date, type='integer', string='Year', multi='dates', readonly=True, store=True),
        'month': fields.function(_set_date, type='integer', string='Month', multi='dates', readonly=True, store=True),
        'day': fields.function(_set_date, type='integer', string='Day', multi='dates', readonly=True, store=True),
        'number': fields.char('Number', required=True, size=40),
        'project_ids': fields.many2many('project.project', 'hse_rules_documents_project_rel', 'doc_id', 'project_id',
                                        'Project', required=True),
        'subject': fields.char('Subject', required=True, size=200),
        'description_id': fields.one2many('hse.rules.documents.description', 'description_id', 'Descriptions'),
        'name_id': fields.many2one('hse.rules.documents.name', 'Name', required=True),
        'title': fields.char('Title', required=True, size=200),
        'attachment_ids': fields.many2many('ir.attachment', 'hse_rules_documents_ir_attachments_rel',
                                           'rules_documents_id', 'attachment_id', 'Attachments'),
    }

    _defaults = {
        'date': fields.date.context_today,
    }


class hse_code_config(osv.osv):
    _name = 'hse.code.config'
    _description = 'Code config'
    _inherit = ["mail.thread"]
    _columns = {
        'model_id': fields.many2one('ir.model', 'Model', required=True, domain=[('model', 'like', 'hse.%')]),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'name': fields.char('Name', required=True, size=150),
    }


class ir_cron(osv.osv):
    _inherit = 'ir.cron'


class hse_hazard_type(osv.osv):
    _name = 'hse.hazard.type'
    _description = 'Types of hazard'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Name', required=True, size=60),
    }
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!')
    ]
    _order = 'name asc'


class hse_risk_rating(osv.osv):
    _name = 'hse.risk.rating'
    _description = 'Risk Rating'
    _inherit = ["mail.thread"]

    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr, uid, ids)[0]
        res[obj.id] = str(obj.rating) + '.  /' + obj.likelihood_id.name + '/  /' + obj.consequence_id.name + '/'
        return res

    _columns = {
        'name': fields.function(_set_name, type='char', string='Name', readonly=True, store=True),
        'rating': fields.integer('Rating'),
        'likelihood_id': fields.many2one('hse.likelihood', 'Likelihood', required=True),
        'consequence_id': fields.many2one('hse.consequence', 'Consequence', required=True),
        'assessment_type': fields.selection(
            [('low_risky', 'Low risky'), ('risky', 'Risky'), ('high_risky', 'High risky')], 'Assessment type',
            required=True),
        'assessment_description': fields.char('Assessment description', size=200),
    }
    _order = 'rating asc'


class hse_consequence(osv.osv):
    _name = 'hse.consequence'
    _description = 'Consequence'
    _inherit = ["mail.thread"]
    _columns = {
        'consequence_rating': fields.integer('Consequence rating'),
        'name': fields.char('Name', required=True, size=50),
        'man_healthy': fields.char('Man healthy', required=True, size=150),
        'env_healthy': fields.char('Env healthy', required=True, size=200),
        'lost_time': fields.char('Lost time', required=True, size=50),
        'asset_damage': fields.char('Asset damage', required=True, size=50),
    }
    _order = 'consequence_rating asc'


class hse_likelihood(osv.osv):
    _name = 'hse.likelihood'
    _description = 'Likelihood'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Likelihood', required=True, size=50),
        'assessment': fields.char('Assessment', required=True, size=30),
        'description': fields.char('Description', required=True, size=150),
    }
    _order = 'assessment asc'


class hse_accident_type(osv.osv):
    _name = 'hse.accident.type'
    _description = 'Types of accidents'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Types of accidents', required=True, size=30, translate=True),
        'value': fields.char('Value', required=True),
    }
    _order = 'name asc'


class hse_accident_category(osv.osv):
    _name = 'hse.accident.category'
    _description = 'Categories of accidents'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Types of accidents', required=True, size=30),
        'accident_id': fields.many2one('hse.accident.type', 'Categories of accidents', required=True),
    }
    _order = 'name asc'


class hse_accident_factor(osv.osv):
    _name = 'hse.accident.factor'
    _description = 'Factors in accidents'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Name', required=True, size=30),
        'type': fields.selection([('immediate_cause', 'Immediate cause'), ('base_cause', 'Base cause')], 'Type',
                                 required=True),

    }
    _order = 'name asc'


class hse_accident_cause(osv.osv):
    _name = 'hse.accident.cause'
    _description = 'Causes of accidents'
    _inherit = ["mail.thread"]
    _columns = {
        'sequence': fields.integer('Sequence'),
        'name': fields.char('Cause', required=True, size=150),
        'factor_id': fields.many2one('hse.accident.factor', 'Factor', required=True),
    }
    _order = 'sequence asc'


class hse_location(osv.osv):
    _name = 'hse.location'
    _description = 'Location'
    _inherit = ["mail.thread"]
    _columns = {
        'name': fields.char('Name', required=True, size=60),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'responsible': fields.many2one('hr.employee', 'Responsible'),
        'department_id': fields.many2one('hr.department', 'Department'),
    }
    _order = 'name asc'


class hse_partner(osv.osv):
    _name = 'hse.partner'
    _description = 'Partner'
    _columns = {
        'name': fields.char('Name', required=True, size=60),
        'project_id': fields.many2one('project.project', 'Project', required=True),
        'email': fields.char('Email', required=True, size=60),
    }
    _order = 'name asc'