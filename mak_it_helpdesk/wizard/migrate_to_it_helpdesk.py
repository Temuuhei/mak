# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import api, models, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class MigrateToItHelpdesk(models.TransientModel):
    _name = 'migrate.to.it.helpdesk'
    _description = "Migrate To IT Helpdesk"

    PROGRAM_SELECTION = [
        ('program', 'Program'),
        ('internet', 'Internet'),
        ('computer', 'Computer'),
        ('printer', 'Printer/Scanner'),
        ('network', 'Network'),
        ('erp', 'ERP'),
        ('email', 'Email'),
        ('spark', 'Spark'),
        ('pitram', 'Pitram'),
    ]

    TYPE_SELECTION = [
        ('service', 'Get service'),
        ('right', 'Get program right'),
        ('pass', 'Change user password')
    ]

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approve', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ]

    dev_helpdesk = fields.Many2one('mak.erp.dev.helpdesk', string='dev_helpdesk')
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    dir = fields.Many2one('res.users', string='Director')
    year = fields.Integer(string='Year')
    month = fields.Integer(string='Month')
    day = fields.Integer(string='Day')
    priority = fields.Selection(string='Priority', selection=[('b', 'Medium'), ('a', 'High')])
    job = fields.Selection(string='Job', selection=PROGRAM_SELECTION)
    type = fields.Selection(string='Type', selection=TYPE_SELECTION)
    description = fields.Text(string='Description')
    state = fields.Selection(string='State', selection=STATE_SELECTION)

    @api.multi
    def action_migrate(self):
        print("##########################################")
        print("##########################################")
        print(self.dev_helpdesk)
        print(self.department_id)
        print(self.employee_id)
        print(self.dir)
        print(self.year)
        print(self.month)
        print(self.day)
        print(self.priority)
        print(self.job)
        print(self.type)
        print(self.description)
        print("##########################################")
        print("##########################################")
        new_mak_it_helpdesk_create_dict = {}
        if self.department_id:
            new_mak_it_helpdesk_create_dict.update(
                {"department_id": self.department_id.id}
            )
        if self.employee_id:
            new_mak_it_helpdesk_create_dict.update(
                {"employee_id": self.employee_id.id}
            )
        if self.dir:
            new_mak_it_helpdesk_create_dict.update(
                {"dir": self.dir.id}
            )
        # if self.year:
        #     new_mak_it_helpdesk_create_dict.update(
        #         {"year": self.year}
        #     )
        # if self.month:
        #     new_mak_it_helpdesk_create_dict.update(
        #         {"month": self.month}
        #     )
        # if self.day:
        #     new_mak_it_helpdesk_create_dict.update(
        #         {"day": self.day}
        #     )
        if self.description:
            new_mak_it_helpdesk_create_dict.update(
                {"description": self.description}
            )
        if self.priority:
            new_mak_it_helpdesk_create_dict.update(
                {"priority": self.priority}
            )
        if self.job:
            new_mak_it_helpdesk_create_dict.update(
                {"job": self.job}
            )
        if self.type:
            new_mak_it_helpdesk_create_dict.update(
                {"type": self.type}
            )
        if self.state == "approve":
            if self.dir:
                new_mak_it_helpdesk_create_dict.update(
                    {"state": 'approve'}
                )
            else:
                new_mak_it_helpdesk_create_dict.update(
                    {"state": 'sent'}
                )
        else:
            new_mak_it_helpdesk_create_dict.update(
                {"state": self.state}
            )
        print("# # # # # # # # # # # # # # # # # # # # # #")
        print("# new_mak_it_helpdesk_create_dict")
        print("# ", new_mak_it_helpdesk_create_dict)
        print("# # # # # # # # # # # # # # # # # # # # # #")
        new_mak_it_helpdesk_create_obj = self.env['mak.it.helpdesk'].create(new_mak_it_helpdesk_create_dict)

        self.dev_helpdesk.write({
            'state': 'cancel',
            'assigned': self.env.uid
        })
        return True
