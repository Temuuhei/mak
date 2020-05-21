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


class mining_plan_line(osv.osv):
    _inherit = 'mining.plan.line'

    _columns = {
        'is_reclamation': fields.boolean('Is Reclamation ?'),
    }
class hse_safety_report(osv.osv_memory):
    _name ='hse.safety.report'
    _description = 'Safety report'
    _columns = {
        'name': fields.char('Name', size=50, readonly=True),
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date', required=True),
        'project_ids': fields.many2many('project.project', 'hse_safety_report_project_rel', 'report_id','project_id', 'Project'),
    }
    
    def get_date_line(self, cr, uid, start_date, end_date, project_ids, context=None):
        hazard = []
        wi = []
        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        cr.execute("select min(to_char(datetime, 'YYYY-MM-DD')) ,count(id) as count from hse_hazard_report where state in ('sent_mail', 'repaired') and project_id in %s and datetime>=%s and datetime<=%s group by to_char(datetime, 'YYYY-MM-DD') order by to_char(datetime, 'YYYY-MM-DD')",
                          (tuple(project_ids), start_date, end_date))
        str_cr = cr.fetchall()
        for item in str_cr:
            hazard.append({'date': item[0], 'cnt': item[1]})

        cr.execute("select date ,count(id) as count from hse_workplace_ispection where state in ('sent_mail', 'repaired') and project_id in %s and date>=%s and date<=%s group by date order by date",
                          (tuple(project_ids), start_date, end_date))

        str_cr = cr.fetchall()
        for item in str_cr:
            wi.append({'date': item[0], 'cnt': item[1]})

        cr.execute("select state,count(state) from hse_hazard_report where state in ('sent_mail', 'repaired') and project_id in %s and datetime>=%s and datetime<=%s group by state",
                            (tuple(project_ids), start_date, end_date))
        str_cr = cr.fetchall()
        hazard_done = 0
        hazard_not_done = 0
        if len(str_cr)>0:
            hazard_done = str_cr[0][1]
        if len(str_cr)>1:
            hazard_not_done = str_cr[1][1]

        cr.execute("select state,count(state) from hse_workplace_ispection where state in ('sent_mail', 'repaired') and project_id in %s and date>=%s and date<=%s group by state",
                            (tuple(project_ids), start_date, end_date))
        str_cr = cr.fetchall()
        wi_done = 0
        wi_not_done = 0
        if len(str_cr)>0:
            wi_done = str_cr[0][1]
        if len(str_cr)>1:
            wi_not_done = str_cr[1][1]

        return {
            'hazard_report': hazard, 
            'workplace_ispection': wi, 
            'hazard_done': hazard_done, 
            'hazard_not_done': hazard_not_done,
            'workplace_done': wi_done,
            'workplace_not_done': wi_not_done}
    def get_man_hour(self, cr, uid, start_date, end_date, project_ids, context=None):
        res = []
        result = []
        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        for item in project_ids:
            data = {}
            data['project_name'] = self.pool.get('project.project').browse(cr, uid, item).name

            cr.execute('SELECT SUM(man_hour::integer) FROM hse_nope_lti '
                            'WHERE date >=%s AND date <= %s AND project_id = %s ',
                          (start_date, end_date, item))
            str_cr = str(cr.fetchone()[0])
            man_hour = 0
            if 'None' not in str_cr:
                man_hour = int(str_cr)
            
            data['mtd'] = man_hour

            cr.execute('SELECT SUM(inc_man_hour::integer) as inc_man_hour FROM hse_nope_lti '
                            'WHERE date = (SELECT max(date) from hse_nope_lti '
                            'WHERE date<=%s and project_id = %s) and project_id = %s ',
                          (end_date, item, item))

            str_cr = str(cr.fetchone()[0])
            man_hour = 0
            if 'None' not in str_cr:
                man_hour = int(str_cr)
            data['ytd'] = man_hour
            result.append(data)
        
        survaljit = []
        # Анхны тусламж
        # Эмнэлгийн тусламж
        # Өмчийн эвдрэл
        # Асгаралт
        # ХЧТА
        data = {}
        sum_cnt = 0        
        for line in project_ids:
            cr.execute("SELECT count(id),string_agg('- '||accident_name,'<br/>') FROM hse_injury_entry "
            "WHERE accident_type in (select id from hse_accident_type where value='FIRST_AID') AND datetime>=%s AND datetime<=%s AND project_id = %s ",
            (start_date, end_date, line))
            str_cr = cr.fetchone()
            sum_cnt += int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name] = int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name+'p'] = str_cr[1]
        data ['Үзүүлэлт']=_('First aid')+'-'+str(sum_cnt)
        survaljit.append(data)

        data = {}
        sum_cnt = 0
        
        for line in project_ids:
            cr.execute("SELECT count(id),string_agg('- '||accident_name,'<br/>') FROM hse_injury_entry "
            "WHERE accident_type in (select id from hse_accident_type where value='MEDICAL_AID') AND datetime>=%s AND datetime<=%s AND project_id = %s ",
            (start_date, end_date, line))
            str_cr = cr.fetchone()
            sum_cnt += int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name] = int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name+'p'] = str_cr[1]
        data ['Үзүүлэлт']=_('Medical aid')+'-'+str(sum_cnt)
        survaljit.append(data)

        
        data = {}
        sum_cnt = 0
        
        for line in project_ids:
            cr.execute("SELECT count(id),string_agg('- '||accident_name,'<br/>') FROM hse_injury_entry "
            "WHERE accident_type in (select id from hse_accident_type where value='PROPERTY_DAMAGE') AND datetime>=%s AND datetime<=%s AND project_id = %s ",
            (start_date, end_date, line))
            str_cr = cr.fetchone()
            sum_cnt += int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name] = int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name+'p'] = str_cr[1]
        data ['Үзүүлэлт']=_('Property damage')+'-'+str(sum_cnt)
        survaljit.append(data)

        data = {}
        sum_cnt = 0
        
        for line in project_ids:
            cr.execute("SELECT count(id),string_agg('- '||accident_name,'<br/>') FROM hse_injury_entry "
            "WHERE accident_type in (select id from hse_accident_type where value='SPILL') AND datetime>=%s AND datetime<=%s AND project_id = %s ",
            (start_date, end_date, line))
            str_cr = cr.fetchone()
            sum_cnt += int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name] = int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name+'p'] = str_cr[1]
        data ['Үзүүлэлт']=_('Spill')+'-'+str(sum_cnt)
        survaljit.append(data)

        data = {}
        sum_cnt = 0
        
        for line in project_ids:
            cr.execute("SELECT count(id),string_agg('- '||accident_name,'<br/>') FROM hse_injury_entry "
            "WHERE is_lti = 't' AND datetime>=%s AND datetime<=%s AND project_id = %s ",
            (start_date, end_date, line))
            str_cr = cr.fetchone()
            sum_cnt += int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name] = int(str_cr[0])
            data[self.pool.get('project.project').browse(cr, uid, line).name+'p'] = str_cr[1]
        data ['Үзүүлэлт']=_('LTI')+'-'+str(sum_cnt)
        survaljit.append(data)
        cr.execute("SELECT count(distinct to_char(datetime, 'YYYY-MM-DD')) FROM hse_injury_entry WHERE accident_type in (select id from hse_accident_type where value not in ('NEAR_MISS_INCIDENT')) AND datetime>=%s AND datetime<=%s AND project_id in %s "
            ,(start_date, end_date, tuple(project_ids)))
        str_cr = cr.fetchone()[0]
        day = (end_date - start_date).days
        safe_day = int(str_cr)
        return {'man_hour': result ,'survaljit':survaljit, 'all_day': day,'safe_day': safe_day}

    def get_rate(self, cr, uid, start_date, end_date, project_ids, context=None):
        lti_frequency = []
        medical_aid_frequency = []
        first_aid_frequency = []
        lti_max = 0
        medical_aid_max = 0
        first_aid_max = 0

        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        cr.execute(
                "select hnl.year,  "
                "(SELECT sum(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='LTI') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT COUNT(hie.id) FROM hse_injury_entry hie WHERE hie.is_lti= 't' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))
        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if lti_max<data['plan']:
                lti_max = data['plan']
            if lti_max<data['frequency']:
                lti_max = data['frequency']
            lti_frequency.append(data)

        cr.execute(
                "select hnl.year,  "
                "(SELECT sum(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='MEDICAL_AID') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT COUNT(hie.id) FROM hse_injury_entry hie WHERE hie.value='MEDICAL_AID' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))
        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if medical_aid_max<data['plan']:
                medical_aid_max = data['plan']
            if medical_aid_max<data['frequency']:
                medical_aid_max = data['frequency']
            medical_aid_frequency.append(data)
        cr.execute(
                "select hnl.year,  "
                "(SELECT sum(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='FIRST_AID') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT COUNT(hie.id) FROM hse_injury_entry hie WHERE hie.value='FIRST_AID' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))
        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if first_aid_max<data['plan']:
                first_aid_max = data['plan']
            if first_aid_max<data['frequency']:
                first_aid_max = data['frequency']
            first_aid_frequency.append(data)

        lti_severity = []
        medical_aid_severity = []
        first_aid_severity = []
        s_lti_max = 0
        s_medical_aid_max = 0
        s_first_aid_max = 0

        cr.execute(
                "select hnl.year,  "
                "(SELECT SUM(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='LTI_LOST_DAY') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT SUM(hie.lost_day) FROM hse_injury_entry hie WHERE hie.is_lti= 't' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))
            
        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if s_lti_max<data['frequency']:
                s_lti_max = data['frequency']
            if s_lti_max<data['plan']:
                s_lti_max = data['plan']
            lti_severity.append(data)

        cr.execute(
                "select hnl.year,  "
                "(SELECT SUM(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='MEDICAL_AID_LOST_DAY') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT SUM(hie.lost_day) FROM hse_injury_entry hie WHERE hie.value= 'MEDICAL_AID' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))

        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if s_medical_aid_max<data['frequency']:
                s_medical_aid_max = data['frequency']
            if s_medical_aid_max<data['plan']:
                s_medical_aid_max = data['plan']

            medical_aid_severity.append(data)

        cr.execute(
                "select hnl.year,  "
                "(SELECT SUM(count) FROM hse_safety_plan hsp WHERE hsp.indicator_id IN (SELECT id FROM hse_safety_indicator WHERE value='FIRST_AID_LOST_DAY') AND hnl.year = hsp.year::INTEGER) as plan,  "
                "SUM(hnl.man_hour::integer) as man_hour, "
                "(SELECT SUM(hie.lost_day) FROM hse_injury_entry hie WHERE hie.value= 'FIRST_AID' AND hie.year = hnl.year and hie.project_id in %s) as freq "
                "from hse_nope_lti hnl "
                "where hnl.project_id in %s and hnl.year<=%s "
                "GROUP BY hnl.year order by hnl.year "
                ,(tuple(project_ids),tuple(project_ids),end_date.year))
           
        str_cr = cr.fetchall()
        for item in str_cr:
            data = {}
            data['year'] = item[0]
            data['plan'] = item[1]
            data['man_hour'] = item[2]
            data['frequency'] = item[3]
            if data['man_hour']==0:
                data['ir'] = 0
            else:
                if data['frequency']==None:
                    data['ir'] = None
                else:
                    data['ir'] = round(float(data['frequency'])*200000/float(data['man_hour']), 2)
            if s_first_aid_max<data['frequency']:
                s_first_aid_max = data['frequency']
            if s_first_aid_max<data['plan']:
                s_first_aid_max = data['plan']
            first_aid_severity.append(data)
        return {
        'lti_frequency': lti_frequency, 
        'medical_aid_frequency': medical_aid_frequency,
        'first_aid_frequency':first_aid_frequency,
        'lti_max': lti_max,
        'medical_aid_max': medical_aid_max,
        'first_aid_max': first_aid_max,
        
        'lti_severity': lti_severity,
        'medical_aid_severity': medical_aid_severity,
        'first_aid_severity': first_aid_severity,
        's_lti_max': s_lti_max,
        's_medical_aid_max': s_medical_aid_max,
        's_first_aid_max': s_first_aid_max,
        }

    def get_indicator(self, cr, uid, start_date, end_date, project_ids, context=None):
        res = []
        hr_project = self.pool.get('hr.department').search(cr, uid, [('project_id','in',project_ids)])
        cr.execute("select array_agg(id), name from hr_department where parent_id in (select id from hr_department where project_id in %s) group by name "
                ,(tuple(project_ids),))
        hr_department = cr.fetchall()
        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        for item in hr_department:
            #  AACX
            #  AБҮ
            #  Зочдын заавар
            #  Давтан сургалт
            #  AМХ
            #  ЭY
            #  OДТ
            data = {}
            send_ok = 0
            data['Place'] = item[1]+' p'
            cr.execute('select count(id) from hse_safety_meeting where project_id in %s AND %s<=date AND date<=%s AND department_id in %s '
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            if int(str_cr)>0:
                send_ok+=1
                data['hse_safety_meeting'] = str_cr
            
            cr.execute('select count(id) from hse_workplace_ispection where project_id in %s AND %s<=date AND date<=%s AND department_id in %s '
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            if int(str_cr)>0:
                send_ok+=1
                data['hse_workplace_ispection'] = str_cr
            
            cr.execute('select count(id) from hse_hazard_report where project_id in %s AND %s<=datetime AND datetime<=%s AND location_id in (select id from hse_location where department_id in %s )'
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['hse_hazard_report'] = str_cr
            cr.execute('select count(id) from hse_risk_assessment where project_id in %s AND %s<=datetime AND datetime<=%s AND location_id in (select id from hse_location where department_id in %s )'
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['hse_risk_assessment'] = str_cr
            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='NEAR_MISS_INCIDENT' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['NEAR_MISS_INCIDENT'] = str_cr
            # Анхны тусламж
            # Эмнэлгийн тусламж
            # Өмчийн эвдрэл
            # Асгаралт
            # ХЧТА

            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='FIRST_AID' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['FIRST_AID'] = str_cr
            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='MEDICAL_AID' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['MEDICAL_AID'] = str_cr
            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='PROPERTY_DAMAGE' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['PROPERTY_DAMAGE'] = str_cr
            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='SPILL' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['SPILL'] = str_cr
            cr.execute("select count(id) from hse_injury_entry where project_id in %s AND %s<=datetime AND datetime<=%s AND department_id in %s AND value='LTI' "
                ,(tuple(project_ids),start_date, end_date, tuple(item[0]) ))
            str_cr = cr.fetchone()[0]
            
            if int(str_cr)>0:
                send_ok+=1
                data['LTI'] = str_cr
            if send_ok>0:
                res.append(data)

       
        return res

    def get_bird_pyramid(self, cr, uid, end_date, project_ids, context=None):
        result = []
        res = {}
        res['lti'] = 1
        res['ma_fa'] = 10
        res['property_damage'] = 30
        res['leading'] = 600
        result.append(res)
        res = {}
        # start_date = datetime.now().strftime('%Y-01-01')

        start_date = str(datetime.strptime(end_date, '%Y-%m-%d').year)+'-01-01'

        date=end_date+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=start_date+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        cr.execute("SELECT COUNT(id) FROM hse_injury_entry WHERE is_lti='t' and project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        
        res['lti'] = cr.fetchone()[0]

        cr.execute("SELECT COUNT(id) FROM hse_injury_entry WHERE value IN ('FIRST_AID','MEDICAL_AID') and project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        res['ma_fa'] = cr.fetchone()[0]

        cr.execute("SELECT COUNT(id) FROM hse_injury_entry WHERE value IN ('PROPERTY_DAMAGE') and project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        res['property_damage'] = cr.fetchone()[0]

        leading = 0
        cr.execute("SELECT COUNT(id) FROM hse_injury_entry WHERE value IN ('NEAR_MISS_INCIDENT') and project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        leading += int(cr.fetchone()[0])

        cr.execute("SELECT COUNT(id) FROM hse_hazard_report WHERE project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        leading += int(cr.fetchone()[0])

        cr.execute("SELECT COUNT(id) FROM hse_workplace_ispection WHERE project_id in %s and date>=%s and date<=%s ",(tuple(project_ids),start_date, end_date))
        leading += int(cr.fetchone()[0])

        cr.execute("SELECT COUNT(id) FROM hse_risk_assessment WHERE project_id in %s and datetime>=%s and datetime<=%s ",(tuple(project_ids),start_date, end_date))
        leading += int(cr.fetchone()[0])

        cr.execute("SELECT COUNT(id) FROM hse_safety_meeting WHERE project_id in %s and date>=%s and date<=%s ",(tuple(project_ids),start_date, end_date))
        leading += int(cr.fetchone()[0])

        res['leading'] = leading
        result.append(res)

        return result

    def get_reclamation(self, cr, uid, start_date, end_date, project_ids, context=None):
        plan_actual = []
        if project_ids:
            cr.execute(
                "select mp.date,sum(mpl.forecast_m3) as plan,  "
                "(select sum(msml.amount_by_measurement) from mining_surveyor_measurement msm  "
                "left join mining_surveyor_measurement_line msml on (msm.id=msml.mining_surveyor_measurement_id) "
                "where msm.date=mp.date and msml.type_measurement ='is_reclamation' group by msm.date) as meas from mining_plan mp "
                "left join mining_plan_line mpl on (mp.id=mpl.plan_id) "
                "where mpl.is_reclamation=true and mp.project_id in %s and mp.date>=%s and mp.date<=%s "
                "group by mp.date order by mp.date "
               ,
               (tuple(project_ids), start_date, end_date))

            str_cr = cr.fetchall()
            monthDict = {1:'1-p cap', 2:'2-p cap', 3:'3-p cap', 4:'4-p cap', 5:'5-p cap', 6:'6-p cap',7:'7-p cap', 8:'8-p cap', 9:'9-p cap', 10:'10-p cap', 11:'11-p cap', 12:'12-p cap'}
            
            for item in str_cr:
                data = {}
                data['Date']=monthDict[datetime.strptime(item[0], '%Y-%m-%d').month]+' '+str(datetime.strptime(item[0], '%Y-%m-%d').day)
                data['Plan']=item[1]
                data['Meas']=item[2]
                plan_actual.append(data)

        return {'plan_actual':plan_actual}

    def _get_project_ids(self, cr, uid, context=None):        
        return self.pool.get('project.project').search(cr, uid, [('members','in',uid)])

    def _get_yesterday(self, cr, uid, context=None):
        date_time = datetime.now()-timedelta(days=1)
        # timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
        # date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
        return date_time.strftime('%Y-%m-%d')

    _defaults = {
        'name': 'Safety report',
        'start_date': datetime.now().strftime('%Y-%m-01'),
        'end_date': _get_yesterday,
        'project_ids': _get_project_ids,
    }