# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime
from openerp import models, fields, api
from openerp.tools.translate import _
from openerp.exceptions import Warning as UserError

DATE_SELECTION = map(lambda x: [x, str(x)], range(1, 32))


class LoanPaymentScheduleCommon(models.AbstractModel):
    _name = "loan.payment_schedule_common"
    _description = "Loan Payment Schedule"
    _order = "schedule_date, id"

    @api.multi
    @api.depends("principle_amount", "interest_amount")
    def _compute_installment(self):
        for payment in self:
            payment.installment_amount = payment.principle_amount + \
                payment.interest_amount

    @api.multi
    def _compute_state(self):
        for payment in self:
            principle_move_line = payment.principle_move_line_id
            interest_move_line = payment.interest_move_line_id
            if not principle_move_line:
                payment.principle_payment_state = "unpaid"
            elif principle_move_line and \
                    not principle_move_line.reconcile_partial_id and \
                    not principle_move_line.reconcile_id:
                payment.principle_payment_state = "unpaid"
            elif principle_move_line.reconcile_partial_id:
                payment.principle_payment_state = "partial"
            elif principle_move_line.reconcile_id:
                payment.principle_payment_state = "paid"

            if not interest_move_line:
                payment.interest_payment_state = "unpaid"
            elif interest_move_line and \
                    not interest_move_line.reconcile_partial_id and \
                    not interest_move_line.reconcile_id:
                payment.interest_payment_state = "unpaid"
            elif interest_move_line.reconcile_partial_id:
                payment.interest_payment_state = "partial"
            elif interest_move_line.reconcile_id:
                payment.interest_payment_state = "paid"

    loan_id = fields.Many2one(
        string="# Loan",
        comodel_name="loan.common",
        ondelete="cascade",
        copy=False,
    )
    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        readonly=True,
        copy=False,
    )
    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        readonly=True,
        copy=False,
    )
    schedule_date = fields.Date(
        string="Schedule Date",
        required=True,
        copy=False,
    )

    paid_date = fields.Date(
        string="Paid Date",
        required=False,
        copy=False,
    )


    pervious_payment_date = fields.Date(
        string="Pervious Payment Date",
        readonly=True,
        states={
            "draft": [
                ("readonly", False),
            ],
        },
    )

    interest_day = fields.Float(
        string="Interest Day",
        required=False,
        copy=False,
    )

    euribor = fields.Float(
        string="EURIBOR",
        required=False,
        copy=False,
    )

    principle_amount = fields.Float(
        string="Principle Amount",
        required=True,
        copy=False,
    )
    interest_amount = fields.Float(
        string="Interest Amount",
        required=True,
        copy=False,
    )
    installment_amount = fields.Float(
        string="Installment Amount",
        compute="_compute_installment",
        store=True,
        copy=False,
    )

    balance_amount = fields.Float(
        string="Balance Amount",
        copy=False,
    )

    other_expense = fields.Float(
        string="Other Expense",
        copy=False,
    )

    undue_interest_amount = fields.Float(
        string="Undue I.A",
        copy=False,
    )

    difference_day = fields.Float(
        string="Fine I.A",
        copy=False,
    )

    principle_payment_state = fields.Selection(
        string="Principle Payment State",
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial Paid"),
            ("paid", "Paid"),
        ],
        compute="_compute_state",
        required=False,
        store=True,
        copy=False,
    )
    interest_payment_state = fields.Selection(
        string="Interest Payment State",
        selection=[
            ("unpaid", "Unpaid"),
            ("partial", "Partial Paid"),
            ("paid", "Paid"),
        ],
        compute="_compute_state",
        required=False,
        store=True,
        copy=False,
    )
    principle_move_line_id = fields.Many2one(
        string="Principle Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
    )
    old_principle_move_line_id = fields.Many2one(
        string="Old Principle Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
    )
    principle_move_id = fields.Many2one(
        string="Principle Move",
        comodel_name="account.move",
        copy=False,
    )
    interest_move_line_id = fields.Many2one(
        string="Interest Move Line",
        comodel_name="account.move.line",
        readonly=True,
        copy=False,
    )
    interest_move_id = fields.Many2one(
        string="Interest Move",
        comodel_name="account.move",
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
        readonly=True,
        copy=False,
    )

    @api.onchange("paid_date","schedule_date")
    def onchange_difference_day(self):
        self.difference_day = 0.0
        print 'temka shdee \n\n\n',type(self.schedule_date),type(self.paid_date),self.schedule_date,self.paid_date
        if self.schedule_date and self.paid_date:
            self.difference_day = (datetime.strptime(self.paid_date, "%Y-%m-%d") - datetime.strptime(self.schedule_date, "%Y-%m-%d")).days

    @api.multi
    def name_get(self):
        res = []
        for schedule in self:
            name = "%s %s" % (
                schedule.loan_id.display_name, schedule.schedule_date)
            res.append((schedule.id, name))
        return res

    @api.multi
    def action_realize_interest(self, date_realization=False):
        for schedule in self:
            schedule._create_interest_realization_move(date_realization)

    @api.multi
    def _get_interest_journal(self):
        self.ensure_one()
        loan = self.loan_id
        journal = loan.type_id.interest_journal_id

        if not journal:
            msg = _("No interest journal defined")
            raise UserError(msg)

        return journal

    @api.multi
    def _prepare_interest_realization_move(self, date_realization=False):
        self.ensure_one()
        if not date_realization:
            date_realization = self.schedule_date
        obj_period = self.env["account.period"]
        loan = self.loan_id
        res = {
            "name": "/",
            "journal_id": self._get_interest_journal().id,
            "date": date_realization,
            "ref": loan.name,
            "period_id": obj_period.find(
                date_realization)[0].id,
        }
        return res

    @api.multi
    def _create_interest_realization_move(self, date_realization):
        self.ensure_one()
        obj_move = self.env[
            "account.move"]
        obj_line = self.env[
            "account.move.line"]

        move = obj_move.sudo().create(
            self._prepare_interest_realization_move(
                date_realization))

        line_receivable = obj_line.sudo().create(
            self._prepare_interest_realization_move_line(
                move))

        self.interest_move_line_id = line_receivable

        obj_line.sudo().create(
            self._prepare_interest_income_move_line(
                move))

    @api.multi
    def _get_realization_move_line_amount(self):
        self.ensure_one()
        debit = credit = 0.0
        loan = self.loan_id
        if loan.direction == "in":
            credit = self.principle_amount
        else:
            debit = self.principle_amount
        return debit, credit

    @api.multi
    def _get_realization_move_line_account(self):
        self.ensure_one()
        dt_today = datetime.now()
        loan = self.loan_id
        dt_schedule = datetime.strptime(self.schedule_date, "%Y-%m-%d")
        account = False
        if abs((dt_schedule - dt_today).days) > 365:
            account = loan.type_id.long_account_principle_id
            if not account:
                msg = _("No long-term principle account defined")
                raise UserError(msg)
        else:
            account = loan.type_id.short_account_principle_id
            if not account:
                msg = _("No short-term principle account defined")
                raise UserError(msg)
        return account

    @api.multi
    def _prepare_principle_receivable_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        name = _("%s %s principle receivable") % (
            loan.name, self.schedule_date)
        debit, credit = \
            self._get_realization_move_line_amount()
        account = \
            self._get_realization_move_line_account()
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": account.id,
            "debit": debit,
            "credit": credit,
            "date_maturity": self.schedule_date,
            "partner_id": loan.partner_id.id,
        }
        return res

    @api.multi
    def _create_principle_receivable_move_line(self, move):
        self.ensure_one()
        line = self.env[
            "account.move.line"].create(
                self._prepare_principle_receivable_move_line(move))
        self.principle_move_line_id = line

    @api.multi
    def _get_interest_realization_move_line_amount(self):
        self.ensure_one()
        debit = credit = 0.0
        loan = self.loan_id
        if loan.direction == "in":
            credit = self.interest_amount
        else:
            debit = self.interest_amount
        return debit, credit

    @api.multi
    def _prepare_interest_realization_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        loan_type = loan.type_id
        name = _("%s %s interest receivable") % (loan.name, self.schedule_date)

        debit, credit = self._get_interest_realization_move_line_amount()

        res = {
            "move_id": move.id,
            "name": name,
            "account_id": loan_type.account_interest_id.id,
            "debit": debit,
            "credit": credit,
            "date_maturity": self.schedule_date,
            "partner_id": loan.partner_id.id,
        }
        return res

    @api.multi
    def _get_interest_move_line_amount(self):
        self.ensure_one()
        debit = credit = 0.0
        loan = self.loan_id
        if loan.direction == "out":
            credit = self.interest_amount
        else:
            debit = self.interest_amount
        return debit, credit

    @api.multi
    def _get_interest_income_account(self):
        self.ensure_one()
        loan = self.loan_id
        account = loan.type_id.account_interest_income_id

        if not account:
            msg = _("No interest income account defined")
            raise UserError(msg)

        return account

    @api.multi
    def _prepare_interest_income_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        name = _("%s %s interest income") % (loan.name, self.schedule_date)
        debit, credit = self._get_interest_move_line_amount()
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": self._get_interest_income_account().id,
            "credit": credit,
            "debit": debit,
            "date_maturity": self.schedule_date,
            "partner_id": self.loan_id.partner_id.id,
        }
        return res

    @api.multi
    def action_long_to_short_term(self):
        for schedule in self:
            if not schedule._check_account_long_to_short_conversion():
                msg = _("Can not convert long term into short term")
                raise UserError(msg)
            schedule.write(schedule._prepare_long_to_short_term())
            schedule._reconcile_long_short()

    @api.multi
    def _reconcile_long_short(self):
        self.ensure_one()
        obj_line = self.env["account.move.line"]
        old_line = self.old_principle_move_line_id
        account = old_line.account_id
        criteria = [
            ("move_id", "=", self.principle_move_id.id),
            ("account_id", "=", account.id)
        ]
        target_line = obj_line.search(criteria)[0]
        (old_line + target_line).reconcile_partial()
        return True

    @api.multi
    def _prepare_long_to_short_term(self):
        self.ensure_one()
        old_move_line = self.principle_move_line_id
        new_move_line = self._create_new_principle_move_line()
        res = {
            "principle_move_line_id": new_move_line.id,
            "old_principle_move_line_id": old_move_line.id,
        }
        return res

    @api.multi
    def _create_new_principle_move_line(self):
        self.ensure_one()
        obj_move = self.env["account.move"]
        obj_line = self.env["account.move.line"]
        move = obj_move.create(
            self._prepare_new_principle_move())
        line = obj_line.create(
            self._prepare_short_new_principle_move_line(move)
        )
        obj_line.create(
            self._prepare_long_new_principle_move_line(move)
        )
        return line

    @api.multi
    def _get_interest_realization_journal(self):
        self.ensure_one()
        loan = self.loan_id
        journal = loan.type_id.realization_journal_id

        if not journal:
            msg = _("No interest realization journal defined")
            raise UserError(msg)

        return journal

    @api.multi
    def _prepare_new_principle_move(self):
        self.ensure_one()
        date_entry = self.schedule_date
        loan = self.loan_id
        obj_period = self.env["account.period"]
        res = {
            "name": "/",
            "journal_id": self._get_interest_realization_journal().id,
            "date": date_entry,
            "ref": loan.name,
            "period_id": obj_period.find(
                date_entry)[0].id,
        }
        return res

    @api.multi
    def _get_short_term_principle_account(self):
        self.ensure_one()
        loan = self.loan_id
        account = loan.type_id.short_account_principle_id

        if not account:
            msg = _("No short-term principle account defined")
            raise UserError(msg)

        return account

    @api.multi
    def _prepare_short_new_principle_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        name = _("%s %s long to short") % (loan.name, self.schedule_date)
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": self._get_short_term_principle_account().id,
            "credit": self.principle_amount,
            "debit": 0.0,
            "date_maturity": self.schedule_date,
            "partner_id": self.loan_id.partner_id.id,
        }
        return res

    @api.multi
    def _get_long_term_principle_account(self):
        self.ensure_one()
        loan = self.loan_id
        account = loan.type_id.long_account_principle_id

        if not account:
            msg = _("No long-term principle account defined")
            raise UserError(msg)

        return account

    @api.multi
    def _prepare_long_new_principle_move_line(self, move):
        self.ensure_one()
        loan = self.loan_id
        name = _("%s %s long to short") % (loan.name, self.schedule_date)
        res = {
            "move_id": move.id,
            "name": name,
            "account_id": self._get_long_term_principle_account().id,
            "debit": self.principle_amount,
            "credit": 0.0,
            "date_maturity": self.schedule_date,
            "partner_id": self.loan_id.partner_id.id,
        }
        return res

    @api.multi
    def _check_account_long_to_short_conversion(self):
        self.ensure_one()
        check = True
        if self.principle_move_line_id.account_id != \
                self.loan_id.type_id.long_account_principle_id:
            check = False
        return check

    @api.model
    def realize_interest_income(self):
        model_name = self._name

        criteria = [
            ("schedule_date", "<=", datetime.now().strftime("%Y-%m-%d")),
            ("state", "=", "active"),
        ]
        obj_schedule = self.env[model_name]
        schedules = obj_schedule.search(criteria)
        schedules.action_realize_interest()
