# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class LoanSelectRealizationEntry(models.TransientModel):
    _name = "loan.select_realization_entry"
    _description = "Select Realization Entry"

    @api.model
    def default_get(self, fields):
        _super = super(LoanSelectRealizationEntry, self)
        res = _super.default_get(fields)
        obj_account_move_line =\
            self.env["account.move.line"]

        loan = self.get_loan()

        move_line_ids =\
            obj_account_move_line.search(
                self._prepare_criteria_move_line(loan))
        res["allowed_move_line_ids"] = move_line_ids.ids

        return res

    allowed_move_line_ids = fields.Many2many(
        string="Allowed Move Lines",
        comodel_name="account.move.line",
    )
    move_line_ids = fields.Many2many(
        string="Move Lines",
        comodel_name="account.move.line",
    )

    @api.multi
    def get_loan(self):
        active_model = self.env.context.get("active_model", False)
        active_id = self.env.context.get("active_id", False)
        loan = self.env[active_model].browse([active_id])[0]
        return loan

    @api.multi
    def _prepare_criteria_move_line(self, loan):
        result = [
            ("id", "=", 0)
        ]

        type_id = loan.type_id
        account_realization_id =\
            type_id.account_realization_id.id

        if type_id.direction == "in":
            result = [
                ("partner_id", "=", loan.partner_id.id),
                ("account_id", "=", account_realization_id),
                ("credit", "=", loan.loan_amount),
                ("reconcile_id", "=", False),
            ]
        else:
            result = [
                ("partner_id", "=", loan.partner_id.id),
                ("account_id", "=", account_realization_id),
                ("debit", "=", loan.loan_amount),
                ("reconcile_id", "=", False),
            ]
        return result

    @api.multi
    def action_select(self):
        self.ensure_one()
        loan = self.get_loan()
        pairs = []
        move_line_header_id = loan.move_line_header_id

        if self.move_line_ids:
            pairs = move_line_header_id + self.move_line_ids
            pairs.reconcile_partial()
