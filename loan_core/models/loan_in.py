# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class LoanIn(models.Model):
    _name = "loan.in"
    _description = "Loan In"
    _inherit = ["loan.common"]

    @api.multi
    @api.depends(
        "move_line_header_id",
        "move_line_header_id.reconcile_id")
    def _compute_realization(self):
        _super = super(LoanIn, self)
        _super._compute_realization()

    payment_schedule_ids = fields.One2many(
        comodel_name="loan.in_payment_schedule",
    )
    type_id = fields.Many2one(
        domain=[
            ("direction", "=", "in"),
        ],
    )
    direction = fields.Selection(
        related="type_id.direction",
        store=True,
    )
    currency_id = fields.Many2one(
        related="type_id.currency_id",
        store=True,
    )
    realized = fields.Boolean(
        compute="_compute_realization",
        store=True,
    )


class LoanInPaymentSchedule(models.Model):
    _name = "loan.in_payment_schedule"
    _inherit = "loan.payment_schedule_common"

    @api.multi
    @api.depends(
        "principle_move_line_id",
        "principle_move_line_id.reconcile_id",
        "principle_move_line_id.reconcile_partial_id",
        "interest_move_line_id",
        "interest_move_line_id.reconcile_id",
        "interest_move_line_id.reconcile_partial_id",
    )
    def _compute_state(self):
        _super = super(LoanInPaymentSchedule, self)
        _super._compute_state()

    loan_id = fields.Many2one(
        comodel_name="loan.in",
    )
    principle_move_id = fields.Many2one(
        comodel_name="account.move",
        related="principle_move_line_id.move_id",
    )
    interest_move_id = fields.Many2one(
        comodel_name="account.move",
        related="interest_move_line_id.move_id",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="loan_id.partner_id",
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="loan_id.currency_id",
        store=False,
    )
    state = fields.Selection(
        related="loan_id.state",
        store=True,
    )
    principle_payment_state = fields.Selection(
        compute="_compute_state",
        store=True,
    )
    interest_payment_state = fields.Selection(
        compute="_compute_state",
        store=True,
    )
