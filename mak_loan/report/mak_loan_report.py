# -*- coding: utf-8 -*-
##############################################################################
#
# Mongolyn Alt MaK LLC, Enterprise Management Solution
# Email : temuujin.ts@mak.mn
# Phone : 976 + 99741074
#
##############################################################################
import base64
from datetime import datetime
import logging
import os
import time
from io import BytesIO

import xlsxwriter
from openerp import models, fields, api, _
from openerp import exceptions
from openerp.addons.l10n_mn_report.tools.report_excel_cell_styles import ReportExcelCellStyles  # @UnresolvedImport


class MakLoanReport(models.TransientModel):
    _name = "mak.loan.report"

    company_id = fields.Many2one('res.company', 'Company')
    loan_id = fields.Many2one('mak.loan', 'Mak Loan')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    @api.multi
    def print_report(self):

        # create workbook
        output = BytesIO()
        book = xlsxwriter.Workbook(output)

        # create name
        report_name = _('Mak Loan Report')
        file_name = "%s_%s.xls" % (report_name, time.strftime('%Y%m%d_%H%M'),)

        # create formats
        format_name = book.add_format(ReportExcelCellStyles.format_name)
        format_filter = book.add_format(ReportExcelCellStyles.format_filter)
        format_filter_right = book.add_format(ReportExcelCellStyles.format_filter_right)
        format_title = book.add_format(ReportExcelCellStyles.format_title)
        format_title_float = book.add_format(ReportExcelCellStyles.format_title_float)
        format_group_left = book.add_format(ReportExcelCellStyles.format_group_left)
        format_group_right = book.add_format(ReportExcelCellStyles.format_group_right)
        format_group_float = book.add_format(ReportExcelCellStyles.format_group_float)
        format_content_center = book.add_format(ReportExcelCellStyles.format_content_center)
        format_content_text = book.add_format(ReportExcelCellStyles.format_content_text)
        format_content_number = book.add_format(ReportExcelCellStyles.format_content_number)
        format_content_float = book.add_format(ReportExcelCellStyles.format_content_float)
        format_content_bold_left = book.add_format(ReportExcelCellStyles.format_content_bold_left)
        format_content_bold_number = book.add_format(ReportExcelCellStyles.format_content_bold_number)

        # create report object
        report_excel_output_obj = self.env['oderp.report.excel.output'].with_context(
            filename_prefix=('mak_loan_report'), form_title=file_name).create({})

        # create sheet
        sheet = book.add_worksheet(time.strftime('%Y-%m-%d'))
        sheet.set_landscape()
        sheet.set_page_view()
        sheet.set_paper(9)  # A4
        sheet.set_margins(0.39, 0.39, 0.39, 0.39)  # 1cm, 1cm, 1cm, 1cm
        sheet.fit_to_pages(1, 0)
        sheet.set_footer('&C&"Times New Roman"&9&P', {'margin': 0.1})

        # compute column
        sheet.set_column('A:A', 4)
        sheet.set_column('B:B', 15)
        sheet.set_column('C:C', 4)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)
        sheet.set_column('F:F', 15)
        sheet.set_column('G:G', 15)
        sheet.set_column('H:H', 15)
        sheet.set_column('I:I', 20)
        sheet.set_column('J:J', 15)
        sheet.set_column('K:K', 15)
        sheet.set_column('L:L', 20)
        sheet.set_column('M:M', 20)
        sheet.set_column('N:N', 20)
        sheet.set_column('O:O', 15)
        sheet.set_column('P:P', 15)
        sheet.set_column('Q:Q', 15)
        sheet.set_column('R:R', 15)
        sheet.set_column('S:S', 15)
        sheet.set_column('T:T', 15)
        sheet.set_column('U:U', 15)
        sheet.set_column('V:V', 15)
        sheet.set_column('W:W', 15)
        sheet.set_column('X:X', 15)
        sheet.set_column('Y:Y', 15)
        sheet.set_column('Z:Z', 15)
        sheet.set_column('AA:AA', 15)
        sheet.set_column('AB:AB', 15)
        seq = 1
        rowx = 6

        col = 0
        sheet.merge_range(rowx, col, rowx + 1, col, _('Seq'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Date'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Day'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Undue Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Total Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Calculation Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Loan Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Total Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Balance Loan'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Add Loan'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Balance Loan'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Calculation Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Other Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Undue Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Loan Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Other Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Undue Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Loan Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Other Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Undue Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Loan Payment'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Interest'), format_title)
        col += 1
        sheet.merge_range(rowx, col, rowx + 1, col, _('Loan'), format_title)


        sheet.merge_range(0, 0, 0, 28, '%s' % self.company_id.name if self.company_id else '', format_filter)
        sheet.merge_range(2, 0, 2, 28, report_name.upper(), format_name)
        sheet.merge_range(4, 0, 4, 28, '%s - %s' % (self.start_date,self.end_date), format_filter_right)
        sheet.merge_range(5, 0, 5, 11, _('Plan Loan'), format_title)
        sheet.merge_range(5, 12, 5, 13, _('Real Performance'), format_title)
        sheet.merge_range(5, 14, 5, 17, _('Payment Order'), format_title)
        sheet.merge_range(5, 18, 5, 21, _('Payment Performance'), format_title)
        sheet.merge_range(5, 22, 5, 25, _('Payment Undue'), format_title)
        sheet.merge_range(5, 26, 5, 27, _('Undue'), format_title)

        where = ''

        if self.loan_id:
            where += ' AND l.loan_id = %s ' % self.loan_id.id

        self.env.cr.execute("SELECT l.id as line_id, p.id as parent_id, l.date as date, l.interest_day as interest_day, l.interest as interest, "
                            "l.undue_interest as undue_interest, l.total_interest as total_interest, l.calc_interest as calc_interest, l.payment_interest as payment_interest, "
                            "l.payment_loan as payment_loan, l.payment_total as payment_total, l.balance_loan as balance_loan, l.add_loan as add_loan, l.zeel_uld as zeel_uld,"
                            "l.huugiin_bod as huugiin_bod, l.tuu_btulbur as tuu_btulbur, l.tuu_nhtulbur as tuu_nhtulbur, l.tuu_hetulult as tuu_hetulult,"
                            "l.tuu_zetulult as tuu_zetulult, l.tg_btulbur as tg_btulbur, l.tg_nhtulbur as tg_nhtulbur, l.tg_hetulult as tg_hetulult,"
                            "l.tg_zetulult as tg_zetulult, l.hhu_btulbur as hhu_btulbur, l.hhu_nhtulbur as hhu_nhtulbur, l.hhu_hetulult as hhu_hetulult,"
                            "l.hhu_zetulult as hhu_zetulult, l.hhh_huu as hhh_huu,"
                            "l.hhh_zeel as hhh_zeel "
                            "FROM mak_loan_line l LEFT JOIN mak_loan p ON l.loan_id = p.id "
                            "WHERE l.date >= %s and l.date <= %s " + where + " ORDER by l.date ASC ", (self.start_date, self.end_date))
        lines = self.env.cr.dictfetchall()

        if lines:
            rowx = 8
            if self.loan_id:
                loan_ids = []
                for line in lines:
                    if line['parent_id'] not in loan_ids:
                        loan_ids.append(line['parent_id'])

                for loan_id in loan_ids:
                    loan = self.env['mak.loan'].browse(loan_id)
                    sheet.merge_range(rowx, 0, rowx, col, loan.name, format_group_left)
                    rowx += 1
                    seq = 1
                    for line in lines:
                        if line['parent_id'] == loan.id:
                            column = 0
                            sheet.write(rowx, column, seq, format_content_number)
                            column += 1
                            sheet.write(rowx, column, line['date'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['interest_day'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['interest'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['undue_interest'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['total_interest'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['calc_interest'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['payment_interest'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['payment_loan'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['payment_total'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['balance_loan'], format_content_text)
                            column += 1
                            sheet.write(rowx, column,  line['add_loan'], format_content_number)
                            column += 1
                            sheet.write(rowx, column, line['zeel_uld'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['huugiin_bod'], format_content_number)
                            column += 1
                            sheet.write(rowx, column, line['tuu_btulbur'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['tuu_nhtulbur'],format_content_number)
                            column += 1
                            sheet.write(rowx, column, line['tuu_hetulult'], format_content_number)
                            column += 1
                            sheet.write(rowx, column, line['tuu_zetulult'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['tg_btulbur'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['tg_nhtulbur'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['tg_hetulult'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['tg_zetulult'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhu_btulbur'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhu_nhtulbur'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhu_hetulult'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhu_zetulult'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhh_zeel'], format_content_text)
                            column += 1
                            sheet.write(rowx, column, line['hhh_huu'], format_content_text)
                            column += 1
                            rowx += 1
                            seq += 1
            else:
                loan_ids = []
                for line in lines:
                    if line['parent_id'] not in loan_ids:
                        loan_ids.append(line['parent_id'])

                for loan_id in loan_ids:
                    loan = self.env['mak.loan'].browse(loan_id)
                    sheet.merge_range(rowx, 0, rowx, col, loan.name, format_group_left)
                    rowx += 1
                seq = 1
                for line in lines:
                    column = 0
                    sheet.write(rowx, column, seq, format_content_number)
                    column += 1
                    sheet.write(rowx, column, line['date'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['interest_day'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['interest'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['undue_interest'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['total_interest'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['calc_interest'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['payment_interest'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['payment_loan'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['balance_loan'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['add_loan'], format_content_number)
                    column += 1
                    sheet.write(rowx, column, line['zeel_uld'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['huugiin_bod'], format_content_number)
                    column += 1
                    sheet.write(rowx, column, line['tuu_btulbur'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['tuu_nhtulbur'], format_content_number)
                    column += 1
                    sheet.write(rowx, column, line['tuu_hetulult'], format_content_number)
                    column += 1
                    sheet.write(rowx, column, line['tuu_zetulult'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['tg_btulbur'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['tg_nhtulbur'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['tg_hetulult'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['tg_zetulult'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['hhu_btulbur'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['hhu_nhtulbur'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['hhu_hetulult'], format_content_text)
                    column += 1
                    sheet.write(rowx, column, line['hhh_zeel'], format_content_text)
                    column += 1
                    rowx += 1
                    seq += 1

        book.close()
        # set file data
        report_excel_output_obj.filedata = base64.encodestring(output.getvalue())

        # call export function
        return report_excel_output_obj.export_report()

