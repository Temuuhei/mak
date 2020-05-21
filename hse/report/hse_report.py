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

class hse_daily_report(osv.osv_memory):
    _name ='hse.daily.report'
    _description = 'Daily report'
    def _set_name(self, cr, uid, ids, name, args, context=None):
        res = {}
        obj = self.browse(cr,uid,ids)[0]
        res[obj.id] = obj.date
        return res
    _columns = {
        'name': fields.function(_set_name, type='char', string='Name', readonly=True, store=True),
        'date': fields.date('Date', required=True),
        'project_ids': fields.many2many('project.project', 'hse_daily_report_project_rel', 'report_id','project_id', 'Project'),
    }
    def get_injury(self, cr, uid, date, project_ids, context=None):
        month = 0
        ytd = 0
        if date and project_ids:
            date_object = datetime.strptime(date, '%Y-%m-%d')

            ytd = len(self.pool.get('hse.injury.entry').search(cr, uid, [('datetime','>=',str(date_object.year)+'-01-01'),('datetime','<=',date),('project_id','in',project_ids),('value','in',('FIRST_AID','MEDICAL_AID'))]))
            month = len(self.pool.get('hse.injury.entry').search(cr, uid, [('year','=',date_object.year),('month','=',date_object.month),('project_id','in',project_ids),('value','in',('FIRST_AID','MEDICAL_AID'))]))
            
        return {'month': month, 'ytd': ytd}
        
    def get_lost_time(self, cr, uid, date, project_ids, context=None):
        ytd = 0
        month = 0
        if date and project_ids:
            date_object = datetime.strptime(date, '%Y-%m-%d')
            year_start = str(str(date_object.year)+'-01-01')
            cr.execute('SELECT sum(mmecl.diff_time) FROM mining_motohour_entry_cause_line mmecl ' 
                        'LEFT JOIN mining_motohour_entry_line mmel ON (mmecl.motohour_cause_id = mmel.id) '
                        'LEFT JOIN mining_daily_entry mde ON (mmel.motohour_id = mde.id) '
                        'WHERE mde.date>=%s AND mde.date<=%s AND mde.project_id in %s AND mmecl.cause_id in (SELECT id FROM mining_motohours_cause WHERE is_injury=true)',
                           (year_start, date, tuple(project_ids)))
            str_cr = str(cr.fetchone()[0])
            
            if 'None' not in str_cr:
                ytd = int(float(str_cr))
            
            cr.execute('SELECT sum(mmecl.diff_time) FROM mining_motohour_entry_cause_line mmecl ' 
                        'LEFT JOIN mining_motohour_entry_line mmel ON (mmecl.motohour_cause_id = mmel.id) '
                        'LEFT JOIN mining_daily_entry mde ON (mmel.motohour_id = mde.id) '
                        'WHERE EXTRACT(YEAR FROM mde.date) = %s AND EXTRACT(MONTH FROM mde.date) = %s AND mde.date<=%s AND mde.project_id in %s AND mmecl.cause_id in (SELECT id FROM mining_motohours_cause WHERE is_injury=true) ',
                           (date_object.year, date_object.month, date, tuple(project_ids)))

            str_cr = str(cr.fetchone()[0])
            
            if 'None' not in str_cr:
                month = int(float(str_cr))
            
        return {'month': month, 'ytd': ytd}
    
    def get_nope_lti(self, cr, uid, date, project_ids, context=None):
        
        if date and project_ids:
            date_object = datetime.strptime(date, '%Y-%m-%d')
            res = []
            lti_id = self.pool.get('hse.nope.lti').search(cr, uid, [])

            monthDict = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
            # monthDict = {1:'1-p Cap', 2:'2-p Cap', 3:'3-p Cap', 4:'4-p Cap', 5:'5-p Cap', 6:'6-p Cap',7:'7-p Cap', 8:'8-p Cap', 9:'9-p Cap', 10:'10-p Cap', 11:'11-p Cap', 12:'12-p Cap'}
            man_hour = 0
            max_lti = 0
            for item in range(1, 13):
                data = {}
                data['Month'] = monthDict[item]
                cr.execute('SELECT SUM(inc_man_hour::integer) as inc_man_hour FROM hse_nope_lti '
                            'WHERE date = (SELECT max(date) from hse_nope_lti '
                            'WHERE year=%s and month=%s and project_id in %s) and project_id in %s ',
                          (date_object.year, item, tuple(project_ids), tuple(project_ids)))
                
                str_cr = cr.fetchone()[0]
                if str_cr != None:
                    man_hour = int(float(str_cr))
                
                data['man_hour'] = man_hour
                
                lti = len(self.pool.get('hse.injury.entry').search(cr, uid, [('year','=',date_object.year),('month','=',item),('project_id','in',project_ids),('is_lti','=',True)]))
                ir = 0.0
                if man_hour != 0:
                    ir = round(float(lti)*200000/float(man_hour), 1)
                
                data['lti'] = lti
                if lti==0:
                    data['lti'] = None
                data['ir'] = ir
                if ir==0:
                    data['ir'] = None
                if max_lti<data['lti']:
                    max_lti = data['lti']
                if max_lti<data['ir']:
                    max_lti = data['ir']
                res.append(data)

            cr.execute('SELECT SUM(inc_man_hour::integer), MAX(inc_total_day::integer) FROM hse_nope_lti WHERE date=%s and project_id in %s',
                          (date, tuple(project_ids)))
            inc_man_hour = 0
            inc_total_day = 0
            str_cr = cr.fetchone()

            if str_cr[0]!=None and str_cr[1]!=None:
                inc_man_hour = int(str_cr[0])
                inc_total_day = int(str_cr[1])
            return {'max_lti': max_lti, 'month_lti': res , 'inc_man_hour': inc_man_hour, 'inc_total_day': inc_total_day}
        return False

    def get_injury_detail(self, cr, uid, date, project_ids, context=None):
        
        if date and project_ids:
            date_object = datetime.strptime(date, '%Y-%m-%d')
            max_injury = 0
            res = []
            accident_type_ids = self.pool.get('hse.accident.type').search(cr, uid, [])

            monthDict = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}

            for item in range(1, 13):
                data = {
                        'Month': monthDict[item],
                    }
                for acc in accident_type_ids:

                    inj_cnt = len(self.pool.get('hse.injury.entry').search(cr, uid, [('year','=',date_object.year),('month','=',item),('project_id','in',project_ids),('accident_type','=',acc)]))
                    data[acc] = inj_cnt
                    if inj_cnt==0:
                        data[acc] = None
                    # else:
                    
                    if max_injury<inj_cnt:
                        max_injury = inj_cnt
                res.append(data)
            all_accident = []
            for item in self.pool.get('hse.accident.type').browse(cr, uid, accident_type_ids):
                trans_id = self.pool.get('ir.translation').search(cr, uid, [('name','=','hse.accident.type,name'),('lang','=',context['lang']),
                                                                       ('src','=',item.name)],
                                                                       limit=1)
                translation = item.name
                if self.pool.get('ir.translation').browse(cr, uid, trans_id):
                    translation = self.pool.get('ir.translation').browse(cr, uid, trans_id)[0].value
                all_accident.append({'id': item.id, 'name': translation})
            
            return {'max_injury': max_injury,'all_injury': res, 'all_accident': all_accident}
        return False

    def get_all_hse(self, cr, uid, date, project_ids, context=None):
        if date and project_ids:
            date +=' 23:59:59'
            date_object = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            res = []
            locations = []
            for item in project_ids:
                send_ok = []
                hutlugch = []
                #  ААСХ
                #  АБҮ
                #  Зочдын заавар
                #  Давтан сургалт
                #  АМХ
                #  ЭҮ
                #  ОДТ
                cr.execute('SELECT count(hsm.id),hd.name FROM hse_safety_meeting hsm LEFT JOIN hr_department hd ON (hd.id = hsm.department_id) '
                'WHERE hsm.year>=%s AND hsm.month>=1 AND hsm.day>=1 AND hsm.date<=%s AND hsm.project_id = %s GROUP BY hd.name',
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                data['Үзүүлэлт']= _('SM')+'-'+str(sum_cnt)
                hutlugch.append(data)

                cr.execute('SELECT count(hwi.id),hd.name FROM hse_workplace_ispection hwi LEFT JOIN hr_department hd ON (hd.id = hwi.department_id) '
                "WHERE hwi.state IN ('sent_mail','repaired') AND hwi.year>=%s AND hwi.month>=1 AND hwi.day>=1 AND hwi.date<=%s AND hwi.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                data['Үзүүлэлт']= _('WPI')+'-'+str(sum_cnt)
                hutlugch.append(data)

                # data = {}
                # sum_cnt = 0
                # data['Үзүүлэлт']= 'Зочдын зааваp-'+str(sum_cnt)
                # hutlugch.append(data)

                # data = {}
                # sum_cnt = 0
                # data['Үзүүлэлт']= 'Давтан сyргалт-'+str(sum_cnt)
                # hutlugch.append(data)

                cr.execute("SELECT count(hhr.id),hl.name FROM hse_hazard_report hhr "
                'LEFT JOIN (SELECT hl.id,CASE WHEN hl.department_id is not null THEN hd.name ELSE hl.name END as name FROM hse_location hl '
                'LEFT JOIN hr_department hd on (hd.id = hl.department_id)) hl on (hl.id=hhr.location_id) '
                "WHERE hhr.state IN ('sent_mail','repaired') AND hhr.year>=%s AND hhr.month>=1 AND "
                'hhr.day>=1 AND hhr.datetime<=%s AND hhr.project_id = %s'
                'GROUP BY hl.name ',(date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                data['Үзүүлэлт']= _('HR')+'-'+str(sum_cnt)
                hutlugch.append(data)

                
                cr.execute("SELECT count(hra.id),hl.name FROM hse_risk_assessment hra "
                'LEFT JOIN (SELECT hl.id,CASE WHEN hl.department_id is not null THEN hd.name ELSE hl.name END as name FROM hse_location hl '
                'LEFT JOIN hr_department hd on (hd.id = hl.department_id)) hl on (hl.id=hra.location_id) '
                "WHERE hra.year>=%s AND hra.month>=1 AND "
                'hra.day>=1 AND hra.datetime<=%s AND hra.project_id = %s'
                'GROUP BY hl.name ',(date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                hutlugch.append(data)
                data['Үзүүлэлт']=_('RA')+'-'+str(sum_cnt)
                
                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.accident_type in (select id from hse_accident_type where value='NEAR_MISS_INCIDENT') AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                hutlugch.append(data)
                data ['Үзүүлэлт']=_('NMI')+'-'+str(sum_cnt)

                survaljit = []
                # Анхны тусламж
                # Эмнэлгийн тусламж
                # Өмчийн эвдрэл
                # Асгаралт
                # ХЧТА
                
                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.accident_type in (select id from hse_accident_type where value='FIRST_AID') AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                survaljit.append(data)
                data ['Үзүүлэлт']=_('FA')+'-'+str(sum_cnt)

                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.accident_type in (select id from hse_accident_type where value='MEDICAL_AID') AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                survaljit.append(data)
                data ['Үзүүлэлт']=_('MA')+'-'+str(sum_cnt)

                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.accident_type in (select id from hse_accident_type where value='PROPERTY_DAMAGE') AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                survaljit.append(data)
                data ['Үзүүлэлт']=_('Pro dam')+'-'+str(sum_cnt)

                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.accident_type in (select id from hse_accident_type where value='SPILL') AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                survaljit.append(data)
                data ['Үзүүлэлт']=_('Spill')+'-'+str(sum_cnt)

                cr.execute('SELECT count(hie.id),hd.name FROM hse_injury_entry hie LEFT JOIN hr_department hd ON (hd.id = hie.department_id) '
                "WHERE hie.year>=%s AND hie.is_lti = 't' AND hie.month>=1 AND hie.day>=1 AND hie.datetime<=%s AND hie.project_id = %s GROUP BY hd.name",
                (date_object.year, date_object, item))
                str_cr = cr.fetchall()
                data = {}
                sum_cnt = 0
                for line in str_cr:
                    send_ok.append(1)
                    data[line[1]] = line[0]
                    sum_cnt += line[0]
                    if line[1] not in locations:
                        locations.append(line[1])
                survaljit.append(data)
                data ['Үзүүлэлт']=_('LTI')+'-'+str(sum_cnt)


                if len(send_ok)>0:
                    res.append({
                        'project_id': item, 
                        'project_name': self.pool.get('project.project').browse(cr, uid, item).name, 
                        'survaljit':survaljit, 'hutlugch':hutlugch, 'locations':locations})
            
            return res
        return False

    def _get_project_ids(self, cr, uid, context=None):
        return self.pool.get('project.project').search(cr, uid, [('members','in',uid)])

    def _get_yesterday(self, cr, uid, context=None):
        date_time = datetime.now()-timedelta(days=1)
        # timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
        # date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
        return date_time.strftime('%Y-%m-%d')

    _defaults = {
        'date': _get_yesterday, 
        'project_ids': _get_project_ids,
    }

class hse_corrective_actions(osv.osv_memory):
    _name ='hse.corrective.actions'
    _description = 'Corrective actions'
    _columns = {
        'name': fields.char('Name', size=50, readonly=True),
        'start_date': fields.date('Start date', required=True),
        'end_date': fields.date('End date', required=True),
        'project_ids': fields.many2many('project.project', 'hse_corrective_actions_project_rel', 'report_id','project_id', 'Project'),
    }
    
    def get_all(self, cr, uid,date_from, date_to, project_ids, context=None):
        not_done = 0
        done = 0
        wi = []
        date=date_to+' 23:59:59'
        end_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        date=date_from+' 00:00:00'
        start_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        if project_ids:
            cr.execute("select count(id) from hse_hazard_report where state in ('sent_mail') and project_id in %s and datetime>=%s and datetime<=%s",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            hazard_not_done = int(str_cr[0])

            cr.execute("select count(id) as count from hse_workplace_ispection where state in ('sent_mail') and project_id in %s and date>=%s and date<=%s",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            wi_not_done = int(str_cr[0])

            cr.execute("select count(id) as count from hse_injury_entry where state in ('closed','sent_mail') and project_id in %s and datetime>=%s and datetime<=%s",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            inj_not_done = int(str_cr[0])

            cr.execute("select count(id) as count from hse_hazard_report where state in ('repaired') and project_id in %s and datetime>=%s and datetime<=%s ",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            hazard_done = int(str_cr[0])

            cr.execute("select count(id) as count from hse_workplace_ispection where state in ('repaired') and project_id in %s and date>=%s and date<=%s ",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            wi_done = int(str_cr[0])

            cr.execute("select count(id) as count from hse_injury_entry where state in ('cor_act_closed') and project_id in %s and datetime>=%s and datetime<=%s ",
                              (tuple(project_ids), start_date, end_date))
            str_cr = cr.fetchone()
            inj_done = int(str_cr[0])
            
            res = []

            base_url= self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url')
            db_name = cr.dbname
            
            
            
            for item in self.pool.get('hse.injury.entry').browse(cr, uid, self.pool.get('hse.injury.entry').search(cr, uid, [('state','=','sent_mail'),('project_id','in',project_ids),('datetime','>=',date_from),('datetime','<=',date_to)])):
                action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_injury_entry')[1]
                for line in item.corrective_action_line:
                    if not line.is_taken:
                        data={}
                        data['uzuulelt']=_('Accident/Incident')
                        data['number']=item.name+u'<br/>'+item.accident_type.name
                        date_time = datetime.strptime(item.datetime, '%Y-%m-%d %H:%M:%S')
                        timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
                        date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
                        data['date']=str(date_time)
                        data['corrective_action']=line.corrective_action_what
                        data['corrective_be_action']=line.how
                        data['when']=str(line.when_start)+' - '+str(line.when_end)
                        members_name = ''
                        members = [x.id for x in line.employee_ids]
                        for jj in members:
                            members_name += self.pool.get('hr.employee').browse(cr, uid, jj).name+'<br/>'
                        members = [x.id for x in line.partner_ids]
                        for jj in members:
                            members_name += self.pool.get('hse.partner').browse(cr, uid, jj).name+'<br/>'

                        data['responsible'] = members_name
                        data['project']=item.project_id.name
                        data['atag']=u'<a href="'+unicode(base_url)+u'/web?db='+unicode(db_name)+u'#id='+str(item.id)+u'&view_type=form&model=hse.injury.entry&action='+str(action_id)+u'" target="_blank" '
                        res.append(data)

            for item in self.pool.get('hse.workplace.ispection').browse(cr, uid, self.pool.get('hse.workplace.ispection').search(cr, uid, [('state','=','sent_mail'),('project_id','in',project_ids),('date','>=',date_from),('date','<=',date_to)])):
                action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_workplace_ispection')[1]
                for line in item.wo_is_line:
                    if not line.is_repaired:
                        data={}
                        data['uzuulelt']=_('Workplace ispection')
                        data['number']=item.name
                        data['date']=item.date
                        data['corrective_action']=line.failure_and_hazard
                        data['corrective_be_action']=line.required_corr_action
                        data['when']=str(line.when_start)+' - '+str(line.when_end)
                        members_name = ''
                        members = [x.id for x in line.employee_ids]
                        for jj in members:
                            members_name += self.pool.get('hr.employee').browse(cr, uid, jj).name+'<br/>'
                        members = [x.id for x in line.partner_ids]
                        for jj in members:
                            members_name += self.pool.get('hse.partner').browse(cr, uid, jj).name+'<br/>'

                        data['responsible'] = members_name
                        data['project']=item.project_id.name
                        data['atag']=u'<a href="'+unicode(base_url)+u'/web?db='+unicode(db_name)+u'#id='+str(item.id)+u'&view_type=form&model=hse.workplace.ispection&action='+str(action_id)+u'" target="_blank" '
                        res.append(data)
            
            
            for item in self.pool.get('hse.hazard.report').browse(cr, uid, self.pool.get('hse.hazard.report').search(cr, uid, [('state','=','sent_mail'),('project_id','in',project_ids),('datetime','>=',date_from),('datetime','<=',date_to)])):
                data={}
                
                data['uzuulelt']=_('Hazard report')
                data['number']=item.name
                data['corrective_action']=item.hazard_identification
                data['corrective_be_action']=item.corrective_action_to_be_taken
                date_time = datetime.strptime(item.datetime, '%Y-%m-%d %H:%M:%S')
                timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
                date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
                data['date']=str(date_time)
                data['when']=''
                data['responsible']=item.responsible.name
                data['project']=item.project_id.name
                action_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'hse', 'action_hse_hazard_report')[1]
                data['atag']=u'<a href="'+unicode(base_url)+u'/web?db='+unicode(db_name)+u'#id='+str(item.id)+u'&view_type=form&model=hse.hazard.report&action='+str(action_id)+u'" target="_blank" '
           
                res.append(data)

            return {
                'done': hazard_done+wi_done+inj_done, 
                'not_done': hazard_not_done+wi_not_done+inj_not_done,
                'result':res,
                'hazard_done': hazard_done, 
                'hazard_not_done': hazard_not_done,
                'workplace_done': wi_done,
                'workplace_not_done': wi_not_done,
                'injury_done': inj_done,
                'injury_not_done': inj_not_done,
                }
        return False
    def _get_project_ids(self, cr, uid, context=None):        
        return self.pool.get('project.project').search(cr, uid, [('members','in',uid)])
    def _get_yesterday(self, cr, uid, context=None):
        date_time = datetime.now()-timedelta(days=1)
        # timezone = pytz.timezone(self.pool.get('res.users').browse(cr , uid, uid).tz)
        # date_time = (date_time.replace(tzinfo=pytz.timezone('UTC'))).astimezone(timezone)
        return date_time.strftime('%Y-%m-%d')
    _defaults = {
        'name': 'Corrective actions',
        'start_date': datetime.now().strftime('%Y-01-01'),
        'end_date': _get_yesterday,
        'project_ids': _get_project_ids,
    }
