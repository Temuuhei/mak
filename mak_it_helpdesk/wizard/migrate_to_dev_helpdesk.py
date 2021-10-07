# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import api, models, fields
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


class MigrateToItHelpdesk(models.TransientModel):
    _name = 'migrate.to.dev.helpdesk'
    _description = "Migrate To Dev Helpdesk"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('approve', 'Approved'),
        ('disapprove', 'Disapproved'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ]

    TYPE_SELECTION = [
        ('error', u'Алдаа'),
        ('imp', u'Сайжруулалт'),
        ('delete', u'Мэдээлэл устгах'),
        ('change', u'Мэдээлэл өөрчилөх'),
        ('new_report', u'Шинэ тайлан'),
    ]

    PRIORITY_SELECTION = [
        ('r', 'Regular'),
        ('m', 'Medium'),
        ('h', 'High')
    ]

    it_helpdesk = fields.Many2one('mak.it.helpdesk', string='it_helpdesk')
    department_id = fields.Many2one('hr.department', string='Department')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    dir = fields.Many2one('res.users', string='Director')
    year = fields.Integer(string='Year')
    month = fields.Integer(string='Month')
    day = fields.Integer(string='Day')
    priority = fields.Selection(string='Priority', selection=PRIORITY_SELECTION, default='r')
    type = fields.Selection(string='Type', selection=TYPE_SELECTION)
    state = fields.Selection(string='State', selection=STATE_SELECTION)
    description = fields.Text(string='Description')

    @api.multi
    def action_migrate(self):
        new_mak_dev_helpdesk_create_dict = {"state": "draft"}
        if self.department_id:
            new_mak_dev_helpdesk_create_dict.update(
                {"department_id": self.department_id.id}
            )
        if self.employee_id:
            new_mak_dev_helpdesk_create_dict.update(
                {"employee_id": self.employee_id.id}
            )
        if self.dir:
            new_mak_dev_helpdesk_create_dict.update(
                {"dir": self.dir.id}
            )
        if self.year:
            new_mak_dev_helpdesk_create_dict.update(
                {"year": self.year}
            )
        if self.month:
            new_mak_dev_helpdesk_create_dict.update(
                {"month": self.month}
            )
        if self.day:
            new_mak_dev_helpdesk_create_dict.update(
                {"day": self.day}
            )
        if self.description:
            new_mak_dev_helpdesk_create_dict.update(
                {"description": self.description}
            )
        if self.priority:
            new_mak_dev_helpdesk_create_dict.update(
                {"priority": self.priority}
            )
        else:
            new_mak_dev_helpdesk_create_dict.update(
                {"priority": 'r'}
            )
        if self.type:
            new_mak_dev_helpdesk_create_dict.update(
                {"type": self.type}
            )

        new_mak_erp_dev_helpdesk_create_obj = self.env['mak.erp.dev.helpdesk'].create(new_mak_dev_helpdesk_create_dict)

        attachment_search_dict = [('res_model', '=', 'mak.it.helpdesk'), ('res_id', '=', self.it_helpdesk.id)]
        exist_attachments = self.env['ir.attachment'].search(attachment_search_dict)
        for exist_attachment in exist_attachments:
            attachment_update_dict = {
                'res_model': 'mak.erp.dev.helpdesk',
                'res_id': new_mak_erp_dev_helpdesk_create_obj.id,
            }
            exist_attachment.write(attachment_update_dict)

        self.it_helpdesk.write({
            'state': 'moved',
            'assigned': self.env.uid
        })
        return True
