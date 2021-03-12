# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp import api, fields, models, _
import logging
from openerp.exceptions import Warning
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger('openerp')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"


class MakLoan(models.Model):
    _name = "mak.loan"
    _inherit = "mail.thread"

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('done', 'Done'),
    ]

    name = fields.Char(string="# Loan", required=True, default="/", readonly=True,
                       states={"draft": [("readonly", False), ], }, copy=False, )

    partner_id = fields.Many2one('res.partner', string = 'Partner')
    company_id = fields.Many2one(string="Company", comodel_name="res.company", required=True,
                                 )
    loan_amount = fields.Float('Loan amount',help='This describe total loan from partner')
    interest = fields.Float('Interest',help='This describe loan s interest from contract')
    undue_interest = fields.Float('Undue Interest' ,help='This describe loan s undue interest from contract')
    interest_period = fields.Integer('Period (interest)')
    first_period_date = fields.Date('First Date of Interest')
    loan_period = fields.Integer('Period (loan)')
    loan_period_amount = fields.Float('Period amount')
    first_loan_date = fields.Date('First Date of Loan')
    date_realization = fields.Date('Realization Date')
    currency_id = fields.Many2one(string="Currency",comodel_name="res.currency",readonly=False,)
    state = fields.Selection([('draft', 'Draft'),('done', 'Done')], string = 'State', default = 'draft', readonly=True, track_visibility='onchange')
    type = fields.Selection([('local', 'Local'),('international', 'International')], string = 'Type', default = 'local')
    line_id = fields.One2many('mak.loan.line','loan_id', string = 'Lines')
    line_zeel_tatalt_id = fields.One2many('mak.loan.zeel.line','loan_id', string = 'Zeel Tatalt Lines')
    line_nemelt_huu_id = fields.One2many('mak.loan.nemelt.huu.line','loan_id', string = 'Nemelt huu Lines')
    line_interest_payment_id = fields.One2many('mak.loan.interest.payment.line','loan_id', string = 'Interest Payment')
    line_loan_payment_id = fields.One2many('mak.loan.loan.payment.line','loan_id', string = 'Loan Payment')
    line_other_payment_id = fields.One2many('mak.loan.other.payment.line','loan_id', string = 'Other Payment')

    @api.multi
    def button_dummy(self):
        print 'Add your logic here'
        return True

    @api.multi
    def action_compute_payment(self):
        line_zeel_tatalt_id = self.env['mak.loan.zeel.line'].search([('loan_id','=', self.id),('computed','=', True)])
        line_nemelt_huu_id = self.env['mak.loan.nemelt.huu.line'].search([('loan_id','=', self.id),('computed','=', True)])
        line_interest_payment_id = self.env['mak.loan.interest.payment.line'].search([('loan_id','=', self.id),('computed','=', True)])
        line_loan_payment_id = self.env['mak.loan.loan.payment.line'].search([('loan_id','=', self.id),('computed','=', True)])
        line_other_payment_id = self.env['mak.loan.other.payment.line'].search([('loan_id','=', self.id),('computed','=', True)])
        if line_zeel_tatalt_id:
            raise Warning((u'Бүртгэлийн алдаа'),
                          (
                          u'Зээл таталт табны бүртгэлийг тооцсон байна. Та бүртгэлээ засна уу. !!.'))
        elif line_nemelt_huu_id:
            raise Warning((u'Бүртгэлийн алдаа'),
                          (
                              u'Нэмэлт хүү табны бүртгэлийг тооцсон байна. Та бүртгэлээ засна уу. !!.'))
        elif line_interest_payment_id:
            raise Warning((u'Бүртгэлийн алдаа'),
                          (
                              u'Хүүгийн төлбөр табны бүртгэлийг тооцсон байна. Та бүртгэлээ засна уу. !!.'))
        elif line_loan_payment_id:
            raise Warning((u'Бүртгэлийн алдаа'),
                          (
                              u'Зээлийн төлбөр табны бүртгэлийг тооцсон байна. Та бүртгэлээ засна уу. !!.'))
        elif line_other_payment_id:
            raise Warning((u'Бүртгэлийн алдаа'),
                          (
                              u'Бусад төлбөр табны бүртгэлийг тооцсон байна. Та бүртгэлээ засна уу. !!.'))
        line = self.env['mak.loan.line']
        interest_line = self.env['mak.loan.interest.payment.line']
        loan_line = self.env['mak.loan.loan.payment.line']
        res = []
        loan_date = datetime.strptime(self.first_loan_date, "%Y-%m-%d")
        period_date = datetime.strptime(self.first_period_date, "%Y-%m-%d")
        next_loan_date = loan_date
        next_interest_date = period_date
        previous_balance_loan = self.loan_amount
        check_loan = 0.0
        interest_total = 0.0
        temka = self.loan_period_amount
        if self.line_id:
            self._cr.execute("""DELETE FROM mak_loan_line WHERE loan_id = %s """ % (self.id,))
            self._cr.execute("""DELETE FROM mak_loan_interest_payment_line WHERE loan_id = %s """ % (self.id,))
            self._cr.execute("""DELETE FROM mak_loan_loan_payment_line WHERE loan_id = %s """ % (self.id,))

        for loan in self:
            line.create({'loan_id':loan.id,
                         'date': loan.date_realization,
                         'balance_loan':loan.loan_amount,
                         'previous_balance_loan':loan.loan_amount,
                         'add_loan':loan.loan_amount
                         })
            i = 0
            while check_loan <= self.loan_amount:
                i += 1
                idate =  datetime.strptime(self.date_realization, "%Y-%m-%d")
                idate += timedelta(days=i)
                payment_interest = 0.0
                payment_loan = 0.0
                add_loan = 0.0
                if idate != next_loan_date and next_interest_date != idate:
                    basic = line.create({'loan_id':self.id,
                                         'date': idate,
                                         'interest_day': 1,
                                         'interest': self.interest,
                                         'undue_interest': self.undue_interest,
                                         'total_interest': self.interest,
                                         'calc_interest': (previous_balance_loan*self.interest)/(365*1)/100,
                                         'payment_interest': payment_interest,
                                         'payment_loan': payment_loan,
                                         'payment_total': payment_loan + payment_interest,
                                         'balance_loan': previous_balance_loan - payment_loan + add_loan,
                                         'previous_balance_loan': previous_balance_loan,
                                         'add_loan': add_loan,
                                         })
                    interest_total += basic.calc_interest
                elif idate == next_loan_date and idate != next_interest_date:
                    check_loan += temka
                    payment_loan = self.loan_period_amount
                    previous_balance_loan = previous_balance_loan - self.loan_period_amount
                    next_loan_date = next_loan_date + relativedelta(months=(12/self.loan_period))
                    if previous_balance_loan > 0.0:
                        period_loan = line.create({'loan_id': loan.id,
                                                    'date': idate,
                                                    'interest_day': 1,
                                                    'interest': self.interest,
                                                    'undue_interest': self.undue_interest,
                                                    'total_interest': self.interest,
                                                    'calc_interest': previous_balance_loan * self.interest / 365 * 1 / 100,
                                                    'payment_interest': payment_interest,
                                                    'payment_loan': payment_loan,
                                                    'payment_total': payment_loan + payment_interest,
                                                    'balance_loan': previous_balance_loan - payment_loan + add_loan,
                                                    'previous_balance_loan': previous_balance_loan,
                                                    'add_loan': add_loan,
                                                    'tuu_hetulult': payment_interest,
                                                    'tuu_zetulult': payment_loan,
                                                    })
                        loan_line.create({'loan_id': loan.id,
                                          'date': idate,
                                          'amount': payment_loan,
                                          'computed': False})
                    else:
                        payment_loan = self.loan_period_amount + previous_balance_loan
                        period_loan = line.create({'loan_id': loan.id,
                                                    'date': idate,
                                                    'interest_day': 1,
                                                    'interest': self.interest,
                                                    'undue_interest': self.undue_interest,
                                                    'total_interest': self.interest,
                                                    'calc_interest': previous_balance_loan * self.interest / 365 * 1 / 100,
                                                    'payment_interest': payment_interest,
                                                    'payment_loan': payment_loan,
                                                    'payment_total': payment_loan + payment_interest,
                                                    'balance_loan': previous_balance_loan - payment_loan + add_loan,
                                                    'previous_balance_loan': previous_balance_loan,
                                                    'add_loan': add_loan,
                                                    'tuu_hetulult': payment_interest,
                                                    'tuu_zetulult': payment_loan,
                                                    })
                        loan_line.create({'loan_id': loan.id,
                                          'date': idate,
                                          'amount': payment_loan,
                                          'computed': False})

                elif idate == next_interest_date and idate != next_loan_date:
                    next_interest_date = next_interest_date + relativedelta(months=(12/self.interest_period))
                    basic = line.create({'loan_id': loan.id,
                                 'date': idate,
                                 'interest_day': 1,
                                 'interest': self.interest,
                                 'undue_interest': self.undue_interest,
                                 'total_interest': self.interest,
                                 'calc_interest': previous_balance_loan*self.interest/365*1/100,
                                 'payment_interest': interest_total + previous_balance_loan*self.interest/365*1/100,
                                 'payment_loan': payment_loan,
                                 'payment_total': payment_loan + interest_total + previous_balance_loan*self.interest/365*1/100,
                                 'balance_loan': previous_balance_loan - payment_loan + add_loan,
                                 'previous_balance_loan': previous_balance_loan,
                                 'add_loan': add_loan,
                                 'tuu_hetulult': interest_total + previous_balance_loan*self.interest/365*1/100,
                                 'tuu_zetulult': payment_loan,
                                 })

                    interest_line.create({'loan_id': loan.id,
                                      'date': idate,
                                      'amount': interest_total + previous_balance_loan*self.interest/365*1/100,
                                      'computed': False})

                    interest_total = 0.0

                elif next_loan_date == idate and next_interest_date == idate:
                    check_loan += temka
                    next_interest_date = next_interest_date + relativedelta(months=(12 / self.interest_period))
                    next_loan_date = next_loan_date + relativedelta(months=(12 / self.loan_period))
                    payment_loan = self.loan_period_amount
                    if previous_balance_loan > self.loan_period_amount:
                        period_loan = line.create({'loan_id': loan.id,
                                                    'date': idate,
                                                    'interest_day': 1,
                                                    'interest': self.interest,
                                                    'undue_interest': self.undue_interest,
                                                    'total_interest': self.interest,
                                                    'calc_interest': previous_balance_loan * self.interest / 365 * 1 / 100,
                                                    'payment_interest': interest_total + previous_balance_loan*self.interest/365*1/100,
                                                    'payment_loan': payment_loan,
                                                    'payment_total': payment_loan + interest_total + previous_balance_loan*self.interest/365*1/100,
                                                    'balance_loan': previous_balance_loan - payment_loan + add_loan,
                                                    'previous_balance_loan': previous_balance_loan,
                                                    'add_loan': add_loan,
                                                   'tuu_hetulult': interest_total + previous_balance_loan * self.interest / 365 * 1 / 100,
                                                   'tuu_zetulult': payment_loan,
                                                    })
                        loan_line.create({'loan_id': loan.id,
                                          'date': idate,
                                          'amount': payment_loan,
                                          'computed': False})

                        interest_line.create({'loan_id': loan.id,
                                              'date': idate,
                                              'amount': interest_total + previous_balance_loan * self.interest / 365 * 1 / 100,
                                              'computed': False})

                        previous_balance_loan = previous_balance_loan - self.loan_period_amount
                        interest_total = 0.0
                    else:
                        payment_loan = previous_balance_loan
                        period_loan = line.create({'loan_id': loan.id,
                                                    'date': idate,
                                                    'interest_day': 1,
                                                    'interest': self.interest,
                                                    'undue_interest': self.undue_interest,
                                                    'total_interest': self.interest,
                                                    'calc_interest': previous_balance_loan * self.interest / 365 * 1 / 100,
                                                    'payment_interest': interest_total + previous_balance_loan*self.interest/365*1/100,
                                                    'payment_loan': payment_loan,
                                                    'payment_total': payment_loan + interest_total + previous_balance_loan*self.interest/365*1/100,
                                                    'balance_loan': 0.0,
                                                    'previous_balance_loan': 0.0,
                                                    'add_loan': add_loan,
                                                   'tuu_hetulult': interest_total + previous_balance_loan * self.interest / 365 * 1 / 100,
                                                   'tuu_zetulult': payment_loan,
                                                    })
                        loan_line.create({'loan_id': loan.id,
                                         'date': idate,
                                         'amount': payment_loan,
                                         'computed': False})

                        interest_line.create({'loan_id': loan.id,
                                              'date': idate,
                                              'amount': interest_total + previous_balance_loan * self.interest / 365 * 1 / 100,
                                              'computed': False})
        return res

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('mak.loan')
        return super(MakLoan, self).create(vals)

class MakLoanLine(models.Model):
    _name = "mak.loan.line"

    loan_id = fields.Many2one('mak.loan', string = 'Parent Loan')
    date = fields.Date('ТХ Огноо')
    interest_day = fields.Integer('ТХ хоног',help='Төлөвлөгөөт хуваарь хүү бодогдох хоног')
    interest = fields.Float('ТХ Суурь хүү', help='Төлөвлөгөөт хуваарь суурь хүү')
    undue_interest = fields.Float('ТХ Нэмэлт', help='Төлөвлөгөөт хуваарь Нэмэлт хүү')
    total_interest = fields.Float('ТХ Нийт хүү', help='Төлөвлөгөөт хуваарь Нийт хүү')
    calc_interest = fields.Float('ТХ Хүү бодолт',help = 'Төлөвлөгөөт хуваарь хүү бодолт')
    payment_interest = fields.Float('ТХ Хүү эргэн төлөлт', help = 'Төлөвлөгөөт хуваарь хүү эргэн төлөлт')
    payment_loan = fields.Float('ТХ Зээл эргэн төлөлт' , help = 'Төлөвлөгөөт хуваарь зээл эргэн төлөлт')
    payment_total = fields.Float('ТХ Нийт төлөлт', help = 'Төлөвлөгөөт хуваарь Нийт төлөлт')
    balance_loan = fields.Float('ТХ Зээлийн үлдэгдэл', help = 'Төлөвлөгөөт хуваарь Зээлийн үлдэгдэл')
    previous_balance_loan = fields.Float('Previous calculation balance of loan', help = 'Same as excel wtf')
    add_loan = fields.Float('ТХ Зээл авсан', help = 'Төлөвлөгөөт хуваарь Зээл авсан')
    zeel_uld = fields.Float('Зээлийн үлдэгдэл', help = 'Бодит гүйцэтгэл Зээлийн үлдэгдэл')
    huugiin_bod = fields.Float('Хүүгийн бодолт', help = 'Бодит гүйцэтгэл Хүүгийн бодолт')
    tuu_btulbur = fields.Float('Бусад төлбөр', help = 'Төлбөрийн үүрэг үүсэлт Бусад төлбөр')
    tuu_nhtulbur = fields.Float('Нэмэгдүүлсэн хүүгийн төлбөр', help = 'Төлбөрийн үүрэг үүсэлт Нэмэгдүүлсэн хүүгийн төлбөр')
    tuu_hetulult = fields.Float('Хүүгийн эргэн төлөлт', help = 'Төлбөрийн үүрэг үүсэлт Хүүгийн эргэн төлөлт')
    tuu_zetulult = fields.Float('Зээл эргэн төлөлт', help = 'Төлбөрийн үүрэг үүсэлт Зээл эргэн төлөлт')
    tg_btulbur = fields.Float('Бусад төлбөр', help='Төлбөрийн гүйцэтгэл Бусад төлбөр')
    tg_nhtulbur = fields.Float('Нэмэгдүүлсэн хүүгийн төлбөр',
                                help='Төлбөрийн гүйцэтгэл Нэмэгдүүлсэн хүүгийн төлбөр')
    tg_hetulult = fields.Float('Хүүгийн эргэн төлөлт', help='Төлбөрийн гүйцэтгэл Хүүгийн эргэн төлөлт')
    tg_zetulult = fields.Float('Зээл эргэн төлөлт', help='Төлбөрийн гүйцэтгэл Зээл эргэн төлөлт')
    hhu_btulbur = fields.Float('Бусад төлбөр', help='Хугацаа хэтэрсэн үлдэгдэл (өсөн нэмэгдэх дүн) Бусад төлбөр')
    hhu_nhtulbur = fields.Float('Нэмэгдүүлсэн хүү',
                               help='Хугацаа хэтэрсэн үлдэгдэл (өсөн нэмэгдэх дүн) Нэмэгдүүлсэн хүүгийн төлбөр')
    hhu_hetulult = fields.Float('Хүүгийн эргэн төлөлт', help='Хугацаа хэтэрсэн үлдэгдэл (өсөн нэмэгдэх дүн) Хүүгийн эргэн төлөлт')
    hhu_zetulult = fields.Float('Зээл эргэн төлөлт', help='Хугацаа хэтэрсэн үлдэгдэл (өсөн нэмэгдэх дүн) Зээл эргэн төлөлт')
    hhh_huu = fields.Float('Хүү', help='Хугацаа хэтэрсэн хоног')
    hhh_zeel = fields.Float('Зээл', help='Хугацаа хэтэрсэн хоног')

    @api.multi
    def button_dummy(self):
        # TDE FIXME: this button is very interesting
        return True

class MakLoanZeelLine(models.Model):
    _name = "mak.loan.zeel.line"


    loan_id = fields.Many2one('mak.loan', string = 'Parent Loan')
    date = fields.Date('Date')
    amount = fields.Char('Amount')
    user_id = fields.Many2one('res.users', string = 'User')
    computed = fields.Boolean('Computed', default =False)

    @api.multi
    def action_compute_zeel(self):
        print 'Zeeliin tatan avaltiig tootsoh'
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            print'max_date',max_date, s.date
            if max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүртгэлээ шалган уу!!.'))
            print' self', self
            s.write({'computed': True,
                     'user_id': self.env.user.id})
            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'add_loan': s.amount})

    @api.multi
    def action_draft(self):
        for s in self:
            s.write({'computed':False,
                     'user_id': self.env.user.id})
        line_ids = self.env['mak.loan.line'].search([('loan_id','=',self.loan_id.id)])
        for line in line_ids:
            if line.date == s.date:
                line.write({'add_loan': 0.0})

class MakLoanNemeltHuuLine(models.Model):
    _name = "mak.loan.nemelt.huu.line"

    loan_id = fields.Many2one('mak.loan', string = 'Parent Loan')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    amount = fields.Float('Amount')
    user_id = fields.Many2one('res.users', string='User')
    computed = fields.Boolean('Computed', default=False)

    @api.multi
    def action_compute_nemelt_huu(self):
        print 'Nemelt huug tootsoh'
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            print'max_date', max_date
            if max_date <= s.start_date or max_date <= s.end_date:
                print' raise 11111'
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүртгэлээ шалган уу!!.'))
            print' self', self
            s.write({'computed': True,
                     'user_id': self.env.user.id})
            add_by_ui = 0.0
            for line in s.loan_id.line_id:
                if line.date >= s.start_date and line.date <= s.end_date:
                    if line.payment_interest > 0:
                        line.update({'undue_interest': s.amount,
                                     'total_interest': line.interest + s.amount,
                                     'calc_interest':  line.previous_balance_loan * (line.interest + s.amount) / 365 * 1 / 100,
                                     'payment_interest': line.payment_interest + add_by_ui,
                                     'payment_total': line.payment_interest + add_by_ui
                                     })
                        add_by_ui = 0.0
                    else:
                        add_by_ui += line.previous_balance_loan * s.amount / 365 * 1 / 100
                        line.update({'undue_interest': s.amount,
                                     'total_interest': line.interest + s.amount,
                                     'calc_interest':  line.previous_balance_loan * (line.interest + s.amount) / 365 * 1 / 100
                                     })
                # else:
                #     print' raise 2222'
                #     raise Warning((u'Өөр огноо сонгоно уу'),
                #                   (
                #                   u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүртгэлээ шалган уу!!.'))

    @api.multi
    def action_draft(self):
        for s in self:
            s.write({'computed': False,
                     'user_id': self.env.user.id})
        add_by_ui = 0.0
        for line in s.loan_id.line_id:
            if line.date >= s.start_date and line.date <= s.end_date:
                if line.payment_interest > 0:
                    line.update({'undue_interest': line.undue_interest - s.amount,
                                 'total_interest': line.interest - s.amount,
                                 'calc_interest': line.previous_balance_loan * (
                                 line.interest + s.amount) / 365 * 1 / 100,
                                 'payment_interest': line.payment_interest - add_by_ui,
                                 'payment_total': line.payment_total - add_by_ui
                                 })
                    add_by_ui = 0.0
                else:
                    add_by_ui += line.previous_balance_loan * s.amount / 365 * 1 / 100
                    line.update({'undue_interest': line.undue_interest - s.amount,
                                 'calc_interest': line.previous_balance_loan * (line.interest + s.amount) / 365 * 1 / 100,
                                 'total_interest': line.interest - s.amount
                                 })

class MakLoanInerestPaymentLine(models.Model):
    _name = "mak.loan.interest.payment.line"

    loan_id = fields.Many2one('mak.loan', string='Parent Loan')
    date = fields.Date('Date')
    amount = fields.Char('Amount')
    user_id = fields.Many2one('res.users', string='User')
    computed = fields.Boolean('Computed', default=False)

    @api.multi
    def action_compute_interest_payment(self):
        print 'Interest payment tootsoh'
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            print'max_date', max_date, s.date
            if max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (
                              u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүргэлээ шалган уу!!.'))
            s.write({'computed': True,
                     'user_id': self.env.user.id})
            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'tg_hetulult': s.amount})

    @api.multi
    def action_draft(self):
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            print'max_date', max_date, s.date
            if max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (
                                  u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүргэлээ шалган уу!!.'))
            s.write({'computed': False,
                     'user_id': self.env.user.id})

            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'tg_hetulult': 0.0})

class MakLoanLoanPaymentLine(models.Model):
    _name = "mak.loan.loan.payment.line"

    loan_id = fields.Many2one('mak.loan', string='Parent Loan')
    date = fields.Date('Date')
    amount = fields.Char('Amount')
    user_id = fields.Many2one('res.users', string='User')
    computed = fields.Boolean('Computed', default=False)

    @api.multi
    def action_compute_loan_payment(self):
        print 'Loan payment tootsoh'
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            if max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (
                              u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүргэлээ шалган уу!!.'))
            s.write({'computed': True,
                     'user_id': self.env.user.id})
            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'tg_zetulult': s.amount})

    @api.multi
    def action_draft(self):
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            if max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (
                                  u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүргэлээ шалган уу!!.'))
            s.write({'computed': False,
                     'user_id': self.env.user.id})

            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'tg_zetulult': 0.0})

class MakLoanOtherPaymentLine(models.Model):
    _name = "mak.loan.other.payment.line"

    loan_id = fields.Many2one('mak.loan', string='Parent Loan')
    date = fields.Date('Date')
    amount = fields.Char('Amount')
    user_id = fields.Many2one('res.users', string='User')
    computed = fields.Boolean('Computed', default=False)

    @api.multi
    def action_compute_other_payment(self):
        print 'Other payment tootsoh'
        for s in self:
            max_date = max(s.loan_id.line_id.mapped('date'))
            print'max_date', max_date, s.date
            if max_date <= s.date or max_date <= s.date:
                raise Warning((u'Өөр огноо сонгоно уу'),
                              (
                              u'Сонгосон огноо нь зээлийн насжилтын хугацаанд хамаарахгүй байгаа тул та бүргэлээ шалган уу!!.'))
            print' self', self
            s.write({'computed': True,
                     'user_id': self.env.user.id})
            for line in s.loan_id.line_id:
                if line.date == s.date:
                    line.write({'tuu_btulbur': s.amount,
                                'tg_btulbur' : s.amount})

    @api.multi
    def action_draft(self):
        for s in self:
            s.write({'computed': False,
                     'user_id': self.env.user.id})

        for line in s.loan_id.line_id:
            if line.date == s.date:
                line.write({'tuu_btulbur': 0.0,
                            'tg_btulbur': 0.0})

























