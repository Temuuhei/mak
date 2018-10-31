# -*- coding: utf-8 -*-

import logging
import psycopg2
import json
import requests
from datetime import datetime, timedelta
import pytz
from tzlocal import get_localzone
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)

class zkDownloadDevice(models.TransientModel):
    _name = 'zk.download.device'
    _description = 'Zk Download Wizard'

    date_from = fields.Date('Date From', required = True)
    date_to = fields.Date('Date To', required = True)
    employee_ids = fields.Many2many('hr.employee', string="Employees")


    @api.multi
    def get_date(self):
        _logger.info(u'<===================== Downloading Attendances ========================>')
        if not self.employee_ids:
            conn = psycopg2.connect("host=192.168.1.102 dbname=timeattden user=postgres password=MakErptimeAtt#@2018")
            cur = conn.cursor()
            cur.execute('SELECT * FROM timetable WHERE inpdate >= %s and inpdate <= %s', (self.date_from,self.date_to))
            all = cur.fetchall()
            conn.close()
            if all:
                for devid, inout, emp_id, inp in all:
                    employee_id = self.env['hr.employee'].search([('otherid', '=', emp_id)], limit=1)
                    if employee_id:
                        self.env.cr.execute(
                            'SELECT device_id,inout,emp_other_id,inpdate FROM zk_main '
                            'WHERE device_id = %s AND '
                            'inout = %s AND '
                            'emp_other_id = %s AND '
                            'inpdate = %s',
                            (devid, inout, emp_id, inp)
                        )
                        ditch = self.env.cr.fetchone()
                        if not ditch:
                            self.env.cr.execute("""
                                                  INSERT INTO zk_main
                                                      (employee_id,
                                                      emp_other_id,
                                                      device_id,
                                                      inout,
                                                      inpdate)
                                                  VALUES
                                                  (%s,%s,%s,%s,%s)
                                              """, (employee_id[0].id, emp_id, devid, inout, inp))

            print '<------------------ Success All ----------------->'
            return True
        else:
            for emp in self.employee_ids:
                conn = psycopg2.connect("host=192.168.1.102 dbname=timeattden user=postgres password=MakErptimeAtt#@2018")
                cur = conn.cursor()
                cur.execute('SELECT * FROM timetable WHERE inpdate >= %s and inpdate <= %s and userid = %s', (self.date_from, self.date_to,emp.otherid))
                one = cur.fetchone()
                all = cur.fetchall()
                employee_id = ''
                conn.close()
                if all:
                    for devid, inout, emp_id, inp in all:
                        employee_id = self.env['hr.employee'].search([('otherid', '=', emp_id)], limit=1)
                        if employee_id:
                            sql = ''
                            self.env.cr.execute(
                                'SELECT device_id,inout,emp_other_id,inpdate FROM zk_main WHERE device_id = %s AND inout = %s AND emp_other_id = %s AND inpdate = %s',
                                (devid, inout, emp_id, inp)
                            )
                            ditch = self.env.cr.fetchone()
                            print 'ditch\n\n\n', ditch
                            if not ditch:
                                self.env.cr.execute("""
                                                                  INSERT INTO zk_main
                                                                      (employee_id,
                                                                      emp_other_id,
                                                                      device_id,
                                                                      inout,
                                                                      inpdate)
                                                                  VALUES
                                                                  (%s,%s,%s,%s,%s)
                                                              """, (employee_id[0].id, emp_id, devid, inout, inp))

            print '<------------------ Success Selected Employees ----------------->'
            return True


    @api.multi
    def delete_date(self):
        _logger.info(u'<===================== Deleting Attendances ========================>')
        if self.date_from and self.date_to:
            if not self.employee_ids:
                self.env.cr.execute("""
                                      DELETE FROM zk_main
                                      WHERE inpdate >= %s and inpdate <= %s
                                                          """, (self.date_from,self.date_to))
                print '<------------------ Deleted ----------------->'
            else:
                for del_ids in self.employee_ids:
                    self.env.cr.execute("""
                                                          DELETE FROM zk_main
                                                          WHERE inpdate >= %s and inpdate <= %s and employee_id = %s
                                                                              """, (self.date_from, self.date_to,del_ids.id))

                print '<------------------ Selected Deleted ----------------->'
            return True

    @api.multi
    def generate_attendance(self):
        _logger.info(u'<===================== Generating Attendances ========================>')
        if self.date_from and self.date_to:
            if not self.employee_ids:
                self.env.cr.execute(
                    'SELECT employee_id,inpdate FROM zk_main WHERE inpdate >= %s and inpdate <= %s',
                    (self.date_from,self.date_to)
                )
                ditch = self.env.cr.fetchall()
                if ditch:
                    for emp,inp in ditch:
                        self.env.cr.execute(
                            'SELECT employee_id,name FROM hr_attendance WHERE employee_id = %s AND name = %s',
                            (emp, inp)
                        )
                        ditch_exist = self.env.cr.fetchone()
                        if not ditch_exist:
                            ddate = inp
                            if datetime.strptime(ddate[0:10] + " 00:00:00", '%Y-%m-%d %H:%M:%S') <= datetime.strptime(
                                    ddate,
                                    '%Y-%m-%d %H:%M:%S') and datetime.strptime(
                                        ddate[0:10] + " 14:00:00", '%Y-%m-%d %H:%M:%S') >= datetime.strptime(ddate,
                                                                                                             '%Y-%m-%d %H:%M:%S'):
                                action = 'sign_in'
                            else:
                                action = 'sign_out'
                            self.env.cr.execute("""
                                                                                       INSERT INTO hr_attendance
                                                                                           (employee_id,
                                                                                           name,
                                                                                           action)
                                                                                       VALUES
                                                                                       (%s,%s,%s)
                                                                                   """, (emp, inp, action))
                            print'++++++++++++++++++++ INSERTED +++++++++++++++++++++++'
                    return True
            else:
                emp_list = []
                for emp in self.employee_ids:
                    self.env.cr.execute(
                        'SELECT employee_id,inpdate FROM zk_main WHERE inpdate >= %s and inpdate <= %s and employee_id = %s',
                        (self.date_from, self.date_to,emp.id)
                    )
                    ditch_picked = self.env.cr.fetchall()
                    if ditch_picked:
                        for emp, inp in ditch_picked:
                                    self.env.cr.execute(
                                        'SELECT employee_id,name FROM hr_attendance WHERE employee_id = %s AND name = %s',
                                        (emp, inp)
                                    )
                                    ditch = self.env.cr.fetchone()
                                    if not ditch:
                                        ddate = inp
                                        if datetime.strptime(ddate[0:10] + " 00:00:00", '%Y-%m-%d %H:%M:%S') <= datetime.strptime(
                                                ddate,
                                                '%Y-%m-%d %H:%M:%S') and datetime.strptime(
                                                    ddate[0:10] + " 14:00:00", '%Y-%m-%d %H:%M:%S') >= datetime.strptime(ddate,
                                                                                                                         '%Y-%m-%d %H:%M:%S'):
                                            action = 'sign_in'
                                        else:
                                            action = 'sign_out'
                                        self.env.cr.execute("""
                                                               INSERT INTO hr_attendance
                                                                   (employee_id,
                                                                   name,
                                                                   action)
                                                               VALUES
                                                               (%s,%s,%s)
                                                           """, (emp, inp, action))
                                        print'++++++++++++++++++++ INSERTED PICKED +++++++++++++++++++++++'
                return True




class zkTmp(models.Model):
    _name = "zk.tmp"
    _description = "Tmp table of zk info"

    device_id = fields.Integer('Device Number')
    inout = fields.Integer('InOut')
    employee_id = fields.Integer('Employee ID')
    inpdate = fields.Datetime('Inp Datetime')



class zkMain(models.Model):
    _name = "zk.main"
    _inherit = ['mail.thread']
    _description = "Zk main table"
    _order = 'inpdate DESC'

    device_id = fields.Integer('Device Number')
    inout = fields.Integer('InOut')
    emp_other_id = fields.Integer('Employee ID')
    employee_id  = fields.Many2one('hr.employee','Employee')
    inpdate = fields.Datetime('Inp Datetime')






