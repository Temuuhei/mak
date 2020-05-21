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
import pytz

class hse_my_safety(osv.osv_memory):
    _name ='hse.my.safety'
    _description = 'My safety'
    _columns = {
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date', required=True),
        'employee_ids': fields.many2many('hr.employee', 'hse_my_safety_employee_rel', 'safety_id','employee_id', 'Employee'),
    }
    def get_training(self, cr, uid, start_date, end_date, employee_ids, context=None):
        sitting_training = []
        stay_training=[]
        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        if employee_ids:
            cr.execute("select p.name,p.date_from from hr_training p left join employee_training_rel r on p.id = r.training_id  where p.date_from >=%s and p.date_to <=%s and r.employee_id in %s group by p.name,p.date_from order by p.date_from",
                               (start_date, end_date, tuple(employee_ids)))
            str_cr = cr.fetchall()
            for item in str_cr:
                data={}
                data['training_name']=item[0]
                data['date']=item[1]
                sitting_training.append(data)

            cr.execute("select p.name,p.date_to from  employee_training_rel s left join hr_training p on (p.id=s.training_id) "
                        "where p.date_to>=%s and s.employee_id in %s order by p.date_to",
                               (datetime.now().strftime('%Y-%m-%d'), tuple(employee_ids)))

            str_cr = cr.fetchall()
            for item in str_cr:
                data={}
                data['training_name']=item[0]
                data['date']=item[1]
                stay_training.append(data)

        return {'sitting_training': sitting_training, 'stay_training': stay_training}

    def get_indicator(self, cr, uid, start_date, end_date, employee_ids, context=None):
        hazard_report = []
        workplace_ispection = []
        accident = []
        safety_meeting = []
        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        if employee_ids:
            cr.execute("select to_char(h.datetime, 'YYYY-MM-DD'),string_agg(distinct '- '||h.hazard_identification,'\n'),count(distinct h.id) "
                        "from hse_hazard_report h where h.datetime>=%s and h.datetime<=%s and "
                        "h.notify_emp_id like %s and substring(h.notify_emp_id, position(',' in h.notify_emp_id)+1)::int in %s group by to_char(h.datetime, 'YYYY-MM-DD') order by to_char(h.datetime, 'YYYY-MM-DD')",
                               (start_date, end_date, "hr.employee%",tuple(employee_ids)))
            str_cr = cr.fetchall()
            monthDict = {1:'1-p cap', 2:'2-p cap', 3:'3-p cap', 4:'4-p cap', 5:'5-p cap', 6:'6-p cap',7:'7-p cap', 8:'8-p cap', 9:'9-p cap', 10:'10-p cap', 11:'11-p cap', 12:'12-p cap'}
            
            for item in str_cr:
                data={}
                data['date']=monthDict[datetime.strptime(item[0], '%Y-%m-%d').month]+' '+str(datetime.strptime(item[0], '%Y-%m-%d').day)

                data['name']=item[1]
                data['count']=item[2]
                hazard_report.append(data)

            cr.execute("select i.date,string_agg(distinct '- '||i.made_place||' '||i.name,'<br/>'),count(distinct i.id) from hse_workplace_ispection_mem_employee_rel r "
                    "full join hse_workplace_ispection i on (r.wo_is_id=i.id) where i.date>=%s and i.date<=%s and r.employee_id in %s or i.captian_id in %s group by i.date order by i.date",
                               (start_date, end_date, tuple(employee_ids),tuple(employee_ids)))
            str_cr = cr.fetchall()
            
            for item in str_cr:
                data={}
                data['date']=monthDict[datetime.strptime(item[0], '%Y-%m-%d').month]+' '+str(datetime.strptime(item[0], '%Y-%m-%d').day)
                data['name']=item[1]
                data['count']=item[2]
                workplace_ispection.append(data)

            cr.execute("select m.date,string_agg(distinct '- '||subject,'<br/>'),count(distinct m.id) from hse_safety_meeting_employee_rel r "
                    "full join hse_safety_meeting m on (r.safety_meeting_id=m.id) "
                    "full join hse_safety_meeting_line l on (m.id=l.safety_meeting_id) "
                    "where m.date>=%s and m.date<=%s and (r.employee_id in %s or participant_id in %s) group by m.date order by m.date",
                               (start_date, end_date, tuple(employee_ids),tuple(employee_ids)))
            str_cr = cr.fetchall()
            
            for item in str_cr:
                data={}
                data['date']=monthDict[datetime.strptime(item[0], '%Y-%m-%d').month]+' '+str(datetime.strptime(item[0], '%Y-%m-%d').day)
                data['name']=item[1]
                data['count']=item[2]
                safety_meeting.append(data)
            
            cr.execute("select  to_char(e.datetime, 'YYYY-MM-DD'),string_agg(distinct '- '||e.accident_name,'<br/>'),count(distinct e.id) from "
                "hse_injury_entry_involved_employee_rel r left join hse_injury_entry e on (r.injury_id= e.id) "
                "where e.datetime>=%s and e.datetime<=%s and r.employee_id in %s group by to_char(e.datetime, 'YYYY-MM-DD') order by to_char(e.datetime, 'YYYY-MM-DD')",
                               (start_date, end_date, tuple(employee_ids)))
            str_cr = cr.fetchall()
            
            for item in str_cr:
                data={}
                data['date']=monthDict[datetime.strptime(item[0], '%Y-%m-%d').month]+' '+str(datetime.strptime(item[0], '%Y-%m-%d').day)
                data['name']=item[1]
                data['count']=item[2]
                accident.append(data)

        return {'hazard_report':hazard_report, 'workplace_ispection':workplace_ispection, 'safety_meeting':safety_meeting, 'accident': accident}
    def _get_employee_ids(self, cr, uid, context=None):
        return self.pool.get('hr.employee').search(cr, uid, [('user_id','=',uid)])

    def _get_yesterday(self, cr, uid, context=None):
        date_time = datetime.now()-timedelta(days=1)
        # timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
        # print 'timezone',timezone
        # date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
        return date_time.strftime('%Y-%m-%d')
    _defaults = {
        'start_date': datetime.now().strftime('2020-01-01'),
        'end_date': _get_yesterday,
        'employee_ids': _get_employee_ids,
    }