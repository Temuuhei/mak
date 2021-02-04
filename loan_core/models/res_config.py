# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class ResConfig(models.TransientModel):
    _name = "loan.config_setting"
    _inherit = "res.config.settings"

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    cron_loan_in_interest_realization_id = fields.Many2one(
        string="Loan In Interest Realization Cron",
        comodel_name="ir.cron",
        related="company_id.cron_loan_in_interest_realization_id",
    )
    cron_loan_out_interest_realization_id = fields.Many2one(
        string="Loan Out Interest Realization Cron",
        comodel_name="ir.cron",
        related="company_id.cron_loan_out_interest_realization_id",
    )
