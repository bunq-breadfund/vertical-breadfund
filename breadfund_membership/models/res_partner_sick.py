# -*- coding: utf-8 -*-

import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _


class ResPartnerSick(models.Model):
    _name = "res.partner.sick"
    _description = "Sick lines for Members"

    currency_id = fields.Many2one(
        'res.currency', related='partner_id.company_id.currency_id',
        string='Company Currency', readonly=True)
    partner_id = fields.Many2one('res.partner')
    name = fields.Char(default='New')
    date_start = fields.Date('Start date', required=True)
    date_end = fields.Date('End date')
    percentage = fields.Float(required=True)
    next_payment_date = fields.Date(
        string='Next payment date', compute='_compute_next_payment_details')
    next_payment_amount = fields.Monetary(
        string='Next payment amount', compute='_compute_next_payment_details')
    payments_made = fields.Integer('Payments made', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                    'res.partner.sick') or _('New')
        ret = super(ResPartnerSick, self).create(vals)
        return ret

    @api.multi
    @api.depends('date_start', 'payments_made')
    def _compute_next_payment_details(self):
        """ Compute details of next sickness payment """
        today = fields.Date.from_string(fields.Date.context_today(self))
        for this in self:
            waiting_days = this.partner_id.company_id.waiting_days or 0
            date_sick_start = fields.Date.from_string(this.date_start)
            date_sick_end = fields.Date.from_string(this.date_end)
            date_paid_sick_start = date_sick_start + relativedelta(days=waiting_days)
            date_sick_until = date_sick_end or today
            amount_month = \
                this.partner_id.member_type_id.monthly_sick_amount * \
                this.percentage / 100.0
            payments_made = this.payments_made
            if not payments_made:
                next_payment_date = date_paid_sick_start + relativedelta(months=1)
                days_paid_sick = (date_sick_until - date_paid_sick_start).days
                days_in_month = (next_payment_date - date_paid_sick_start).days
                factor = max(0.0, min(1.0, (days_paid_sick / days_in_month)))
                next_payment_amount = factor * amount_month
            else:
                prev_payment_date = date_paid_sick_start + relativedelta(months=payments_made)
                if date_sick_until > prev_payment_date:
                    next_payment_date = date_paid_sick_start + timedelta(month=1 + payments_made)
                    days_paid_sick = (date_sick_until - prev_payment_date).days
                    days_in_month = (next_payment_date - prev_payment_date).days
                    factor = max(0.0, min(1.0, (days_paid_sick / days_in_month)))
                    next_payment_amount = factor * amount_month
                else:
                    next_payment_date = None
                    next_payment_amount = None
            this.next_payment_date = next_payment_date
            this.next_payment_amount = next_payment_amount
