# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
import logging
from datetime import datetime

_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class LoanOut(models.Model):
    _name = "loan.out"
    _description = "Loan Out"
    _inherit = ["loan.common"]

    @api.multi
    @api.depends(
        "move_line_header_id",
        "move_line_header_id.reconcile_id")
    def _compute_realization(self):
        _super = super(LoanOut, self)
        _super._compute_realization()

    payment_schedule_ids = fields.One2many(
        comodel_name="loan.out_payment_schedule",
    )
    type_id = fields.Many2one(
        domain=[
            ("direction", "=", "out"),
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

# Шинэ table үүсгэв
class Loan(models.Model):
    _name = "loan"

    name = fields.Char(string="# Loan",required=True,default="/",readonly=True,states={"draft": [("readonly", False),],},copy=False,)
    company_id = fields.Many2one(string="Company",comodel_name="res.company",required=True,default=lambda self: self._default_company_id(),)
    partner_id = fields.Many2one(string="Partner",comodel_name="res.partner",required=True,readonly=True,domain=["|",
            "&",
            ("parent_id", "=", False),
            ("is_company", "=", False),
            ("is_company", "=", True),
        ],
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    request_date = fields.Date(
        string="Realization Request Date",
        required=True,
        default=fields.Date.today(),
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    date_realization = fields.Date(
        string="Realization Date",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        copy=False,
    )
    type_id = fields.Many2one(
        string="Loan Type",
        comodel_name="loan.type",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    direction = fields.Selection(
        string="Direction",
        selection=[
            ("in", "In"),
            ("out", "Out"),
        ],
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        readonly=False,
    )
    loan_amount = fields.Float(
        string="Loan Amount",
        required=True,
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    interest = fields.Float(
        string="Interest (p.a)",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    undue_interest = fields.Float(
        string="Undue Interest (p.a)",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    maximum_installment_period = fields.Integer(
        string="Maximum Installment Period",
        readonly=True,
        copy=False,
    )
    manual_loan_period = fields.Integer(
        string="Loan Period",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        required=True,
    )

    manual_interest_period = fields.Integer(
        string="Interest Period",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        required=True,
    )

    state = fields.Selection(
        string="State",
        selection=[
            ("draft", "Draft"),
            ("confirm", "Waiting for Approval"),
            ("approve", "Waiting for Realization"),
            ("active", "Active"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        required=True,
        readonly=True,
        copy=False,
    )

class LoanOutPaymentScheduleDetail(models.Model):
    _name = "loan.out_payment_schedule_detail"



    @api.multi
    @api.depends('main_interest','add_interest')
    def _compute_total_interest(self):
        print 'Compute Total Interest'
        for rec in self:
            rec.total_interest = rec.main_interest + rec.add_interest
            print 'rec.total_interest',rec.total_interest

    @api.multi
    @api.depends('date','interest_day','total_interest','pervious_loan')
    def _calculation_interest(self):
        print 'Calculated By Interest'
        days = 365 # Mostly year's day count
        for rec in self:
            date_object = datetime.strptime(rec.date, '%Y-%m-%d')
            year = date_object.year
            if year % 400 == 0:
                days += 1
            elif year % 4 == 0 and year % 100 != 0:
                days += 1
            rec.calc_by_interest = rec.pervious_loan * rec.total_interest / days * rec.interest_day

    loan_id = fields.Many2one(
        string="# Loan",
        comodel_name="loan",
        ondelete="cascade",
        copy=False,
    )
    date = fields.Date('Date')
    interest_day = fields.Integer('Interest day')
    main_interest = fields.Float('Main Interest')
    add_interest = fields.Float('Additional Interest')
    total_interest = fields.Float('Total Interest',compute="_compute_total_interest", store=True)
    calc_by_interest = fields.Float('Calculated by total interest', compute = "_calculation_interest", store=True)
    interest_payment = fields.Float('Interest Payment')
    loan_payment = fields.Float('Loan Payment')
    total_payment = fields.Float('Total Payment')
    balance_loan = fields.Float('Balance Loan')
    pervious_loan = fields.Float('Pervious Loan')

    # @api.onchange('acc_number', 'partner_id', 'acc_type')
    # def _onchange_set_l10n_ch_postal(self):
    #     if self.acc_type == 'iban':
    #         self.l10n_ch_postal = self._retrieve_l10n_ch_postal(self.sanitized_acc_number)
    #     elif self.acc_type == 'postal':
    #         if self.acc_number and " " in self.acc_number:
    #             self.l10n_ch_postal = self.acc_number.split(" ")[0]
    #         else:
    #             self.l10n_ch_postal = self.acc_number
    #             # In case of ISR issuer, this number is not
    #             # unique and we fill acc_number with partner
    #             # name to give proper information to the user
    #             if self.partner_id and self.acc_number[:2] in ["01", "03"]:
    #                 self.acc_number = ("{} {}").format(self.acc_number, self.partner_id.name)

class LoanOutPaymentSchedule(models.Model):
    _name = "loan.out_payment_schedule"
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
        _super = super(LoanOutPaymentSchedule, self)
        _super._compute_state()

    loan_id = fields.Many2one(
        comodel_name="loan.out",
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
