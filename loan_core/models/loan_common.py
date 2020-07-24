# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError
from datetime import datetime

DATE_SELECTION = map(lambda x: [x, str(x)], range(1, 32))


class LoanCommon(models.AbstractModel):
    _name = "loan.common"
    _description = "Abstract Model for Loan"
    _inherit = [
        "mail.thread",
        "base.sequence_document",
        "base.workflow_policy_object",
    ]

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    @api.multi
    @api.depends(
        "payment_schedule_ids",
        "payment_schedule_ids.principle_amount",
        "payment_schedule_ids.interest_amount"
    )
    def _compute_total(self):
        for loan in self:
            loan.total_principle_amount = 0.0
            loan.total_interest_amount = 0.0
            if loan.payment_schedule_ids:
                for schedule in loan.payment_schedule_ids:
                    loan.total_principle_amount += schedule.principle_amount
                    loan.total_interest_amount += schedule.interest_amount

    @api.multi
    def _compute_realization(self):
        for loan in self:
            loan.realized = False
            if not loan.move_line_header_id:
                continue
            if loan.move_line_header_id.reconcile_id:
                loan.realized = True

    @api.multi
    @api.depends(
        "type_id",
    )
    def _compute_policy(self):
        _super = super(LoanCommon, self)
        _super._compute_policy()

    name = fields.Char(
        string="# Loan",
        required=True,
        default="/",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        copy=False,
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=lambda self: self._default_company_id(),
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        domain=[
            "|",
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
    maximum_loan_amount = fields.Float(
        string="Maximum Loan Amount",
        readonly=True,
        copy=False,
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



    manual_principle_period = fields.Integer(
        string="Principle Period",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
        required=True,
    )

    annual_amount = fields.Integer(
        string="Annual Amount",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        }

    )

    first_payment_date = fields.Date(
        string="First Interest Payment Date",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )


    first_principle_payment_date = fields.Date(
        string="First Principle Payment Date",
        readonly=True,
        required=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )
    total_principle_amount = fields.Float(
        string="Total Principle Amount",
        compute="_compute_total",
        store=True,
    )
    total_interest_amount = fields.Float(
        string="Total Interest Amount",
        compute="_compute_total",
        store=True,
    )
    realized = fields.Boolean(
        string="Realized",
        compute="_compute_realization",
        store=True,
    )
    payment_schedule_ids = fields.One2many(
        string="Payment Schedules",
        comodel_name="loan.payment_schedule_common",
        inverse_name="loan_id",
        copy=False,
    )
    confirm_date = fields.Datetime(
        string="Confirm Date",
        readonly=True,
        copy=False,
    )
    confirm_uid = fields.Many2one(
        string="Confirm By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    approve_date = fields.Datetime(
        string="Approve Date",
        readonly=True,
        copy=False,
    )
    approve_uid = fields.Many2one(
        string="Approve By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    realization_date = fields.Datetime(
        string="Realization Date",
        readonly=True,
        copy=False,
    )
    realization_uid = fields.Many2one(
        string="Realized By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    done_date = fields.Date(
        string="Done Date",
        readonly=True,
        copy=False,
    )
    done_uid = fields.Many2one(
        string="Done By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    cancel_date = fields.Date(
        string="Cancel Date",
        readonly=True,
        copy=False,
    )
    cancel_uid = fields.Many2one(
        string="Cancel By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
    )
    manual_realization = fields.Boolean(
        string="Manual Realization",
        copy=False,
    )
    move_realization_id = fields.Many2one(
        string="Realization Journal Entry",
        comodel_name="account.move",
        readonly=True,
        copy=False,
    )
    move_line_header_id = fields.Many2one(
        string="Realization Move Line Header",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
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
    # Policy Fields
    confirm_ok = fields.Boolean(
        string="Can Confirm",
        compute="_compute_policy",
    )
    approve_ok = fields.Boolean(
        string="Can Approve",
        compute="_compute_policy",
    )
    cancel_ok = fields.Boolean(
        string="Can Cancel",
        compute="_compute_policy",
    )
    restart_ok = fields.Boolean(
        string="Can Restart",
        compute="_compute_policy",
    )

    @api.multi
    @api.constrains("maximum_loan_amount", "loan_amount")
    def _check_loan_amount(self):
        for loan in self:
            if loan.loan_amount <= 0.0:
                strWarning = _("Loan amount has to be greater than 0")
                raise models.ValidationError(strWarning)

            if loan.loan_amount > loan.maximum_loan_amount:
                strWarning = _("Loan amount exceed maximum loan amount")
                raise models.ValidationError(strWarning)

    @api.multi
    @api.constrains("maximum_installment_period", "manual_loan_period")
    def _check_loan_period(self):
        for loan in self:
            if loan.manual_loan_period <= 0:
                strWarning = _("Loan period has to be greated than 0")
                raise models.ValidationError(strWarning)
            if loan.manual_loan_period > loan.maximum_installment_period:
                strWarning = _("Loan period exceed maximum installment period")
                raise models.ValidationError(strWarning)

    @api.model
    def create(self, values):
        _super = super(LoanCommon, self)
        result = _super.create(values)
        sequence = result._create_sequence()
        result.write({
            "name": sequence,
        })
        return result

    @api.multi
    def unlink(self):
        for loan in self:
            strWarning = _("""You can not delete loan %s. \n
                         Loan can be deleted only on cancel state and
                         has not been assigned a
                         loan number""") % loan.display_name
            if (loan.state != "cancel" or
                    loan.name != "/") and \
                    not self.env.context.get("force_unlink", False):
                raise UserError(strWarning)
        return super(LoanCommon, self).unlink()

    @api.multi
    def button_dummy(self):
        for line in self.payment_schedule_ids:
            print 'Line \n',line
            if line.schedule_date <> line.paid_date:
                diff = (datetime.strptime(line.paid_date, "%Y-%m-%d") - datetime.strptime(line.schedule_date, "%Y-%m-%d")).days
                undue_total = (line.balance_amount*(self.interest+line.euribor))/100/365*diff
                diff_total = (line.principle_amount*(self.interest+line.euribor)*(self.undue_interest/100))/100/365*diff
                line.write({'undue_interest_amount': undue_total,'difference_day': diff_total,})
            else:
                line.write({'undue_interest_amount': 0.0, })
            interest_amount = (line.balance_amount * (self.interest + line.euribor)) / 100 / 365 * line.interest_day
            line.write({'interest_amount': interest_amount, })


        # if self.cost_approve_ids:
        #     for expense in self.cost_approve_ids:
        #         for price in expense.item_ids:
        #             price.write({'price_unit': amount})
        return True

    @api.multi
    def action_compute_payment(self):
        print'111111111111111111111'
        for loan in self:
            loan._compute_payment()

    @api.multi
    def _compute_payment(self):
        print  '222222222'
        self.ensure_one()
        schedule_object_name = self.payment_schedule_ids._name
        print 'schedule_object_name',schedule_object_name
        obj_payment = self.env[schedule_object_name]
        obj_loan_type = self.env["loan.type"]

        self.payment_schedule_ids.unlink()
        print 'deleted'
        payment_datas = self.type_id._compute_interest(self.loan_amount,
            self.interest,
            self.undue_interest,
            self.annual_amount,
            self.manual_loan_period,
            self.first_payment_date,
            self.first_principle_payment_date,
            self.request_date,
            self.manual_interest_period,
            self.manual_principle_period,
            self.type_id.interest_method)
        print  'payment_datas',payment_datas
        if payment_datas:
            for payment_data in payment_datas:
                payment_data.update({"loan_id": self.id})
                obj_payment.create(payment_data)

    @api.multi
    def workflow_action_confirm(self):
        for loan in self:
            data = loan._prepare_confirm_data()
            loan.write(data)

    @api.multi
    def workflow_action_approve(self):
        for loan in self:
            loan._compute_payment()
            data = loan._prepare_approve_data()
            loan.write(data)

    @api.multi
    def workflow_action_active(self):
        for loan in self:
            data = loan._prepare_active_data()
            loan.write(data)

    @api.multi
    def workflow_action_done(self):
        for loan in self:
            data = loan._prepare_done_data()
            loan.write(data)

    @api.multi
    def workflow_action_cancel(self):
        for loan in self:
            if not loan._can_cancel():
                strWarning = _("Loan can only be cancelled on "
                               "draft, waiting for approval or "
                               "ready to be process state")
                raise models.ValidationError(strWarning)
            loan._delete_receivable_move()
            data = loan._prepare_cancel_data()
            loan.write(data)

    @api.multi
    def _prepare_confirm_data(self):
        self.ensure_one()
        return {
            "state": "confirm",
            "confirm_date": fields.datetime.now(),
            "confirm_uid": self.env.user.id,
        }

    @api.multi
    def _can_cancel(self):
        self.ensure_one()
        if self.state not in ("draft", "confirm", "approve"):
            return False
        else:
            return True

    @api.multi
    def _prepare_approve_data(self):
        self.ensure_one()
        move_id, move_line_header_id = self._create_realization_move()
        data = {
            "state": "approve",
            "approve_date": fields.datetime.now(),
            "approve_uid": self.env.user.id,
            "move_realization_id": move_id,
            "move_line_header_id": move_line_header_id,
        }

        if not self.date_realization:
            data.update({
                "date_realization": fields.datetime.now(),
            })
        return data

    @api.multi
    def _create_realization_move(self):
        self.ensure_one()
        obj_move = self.env[
            "account.move"]
        obj_line = self.env[
            "account.move.line"]

        move = obj_move.sudo().create(
            self._prepare_realization_move())

        move_line_header = obj_line.sudo().create(
            self._prepare_header_move_line(move))

        for schedule in self.payment_schedule_ids:
            schedule._create_principle_receivable_move_line(move)

        debit = credit = 0.0
        for line in move.line_id:
            debit += line.debit
            credit += line.credit

        if debit != credit:
            amount = abs(debit - credit)
            obj_line.sudo().create(
                self._prepare_rounding_move_line(move, amount))

        return move.id, move_line_header.id

    @api.multi
    def _delete_receivable_move(self):
        self.ensure_one()
        if self.move_realization_id:
            self.move_realization_id.unlink()

    @api.multi
    def _prepare_active_data(self):
        self.ensure_one()
        return {
            "state": "active",
            "date_realization": fields.datetime.now(),
            "realization_date": fields.datetime.now(),
            "realization_uid": self.env.user.id,
        }

    @api.multi
    def _prepare_done_data(self):
        self.ensure_one()
        return {
            "state": "done",
            "done_date": fields.datetime.now(),
            "done_uid": self.env.user.id,
        }

    @api.multi
    def _prepare_cancel_data(self):
        self.ensure_one()
        return {
            "state": "cancel",
            "cancel_date": fields.datetime.now(),
            "cancel_uid": self.env.user.id,
        }

    @api.multi
    def _get_realization_journal(self):
        self.ensure_one()
        journal = self.type_id.realization_journal_id

        if not journal:
            msg = _("No realization journal defined")
            raise UserError(msg)

        return journal

    @api.multi
    def _prepare_realization_move(self):
        self.ensure_one()
        obj_period = self.env["account.period"]
        if not self.date_realization:
            date_realization = fields.datetime.now()
        else:
            date_realization = self.date_realization

        res = {
            "name": "/",
            "journal_id": self._get_realization_journal().id,
            "date": date_realization,
            "ref": self.name,
            "period_id": obj_period.find(
                self.date_realization)[0].id,
        }
        return res

    @api.multi
    def _get_realization_move_line_header_amount(self):
        self.ensure_one()
        debit = credit = 0.0
        if self.direction == "out":
            credit = self.total_principle_amount
        else:
            debit = self.total_principle_amount
        return debit, credit

    @api.multi
    def _get_realization_account(self):
        self.ensure_one()
        account = self.type_id.account_realization_id

        if not account:
            msg = _("No realization account defined")
            raise UserError(msg)

        return account

    @api.multi
    def _prepare_header_move_line(self, move):
        self.ensure_one()
        name = _("%s loan realization") % (self.name)
        debit, credit = \
            self._get_realization_move_line_header_amount()
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": self._get_realization_account().id,
            "debit": debit,
            "credit": credit,
            "partner_id": self.partner_id.id,
        }
        return res

    @api.multi
    def _get_rounding_account(self):
        self.ensure_one()
        account = self.type_id.account_rounding_id

        if not account:
            msg = _("No rounding account defined")
            raise UserError(msg)

        return account

    @api.multi
    def _prepare_rounding_move_line(self, move, amount):
        self.ensure_one()
        name = _("%s loan rounding") % (self.name)
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": self._get_rounding_account().id,
            "debit": 0.0,
            "credit": amount,
            "partner_id": self.partner_id.id,
        }
        return res

    @api.onchange("type_id")
    def onchange_maximum_loan_amount(self):
        self.maximum_loan_amount = 0.0
        if self.type_id:
            self.maximum_loan_amount = self.type_id.maximum_loan_amount

    @api.onchange("type_id")
    def onchange_maximum_installment_period(self):
        self.maximum_installment_period = 0.0
        if self.type_id:
            self.maximum_installment_period = \
                self.type_id.maximum_installment_period

    @api.onchange("type_id")
    def onchange_interest(self):
        self.interest = 0.0
        if self.type_id:
            self.interest = self.type_id.interest_amount
