# -*- coding: utf-8 -*-
# Copyright 2019 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade
from openerp import api, SUPERUSER_ID


def migrate_first_payment_date_loan_in(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loan_in as a
        SET first_payment_date=(
            SELECT b.schedule_date
            FROM loan_in_payment_schedule AS b
            WHERE b.loan_id=a.id
            ORDER BY b.schedule_date
            LIMIT 1
        );
        """)


def migrate_first_payment_date_loan_out(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE loan_out as a
        SET first_payment_date=(
            SELECT b.schedule_date
            FROM loan_out_payment_schedule AS b
            WHERE b.loan_id=a.id
            ORDER BY b.schedule_date
            LIMIT 1
        );
        """)


@openupgrade.migrate()
def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    openupgrade.drop_columns(
        cr,
        [("loan_in", "date_payment")]
    )
    openupgrade.drop_columns(
        cr,
        [("loan_out", "date_payment")]
    )
    migrate_first_payment_date_loan_in(env)
    migrate_first_payment_date_loan_out(env)
