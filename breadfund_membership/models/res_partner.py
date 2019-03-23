# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATE = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed')
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection(STATE, default='draft')
    bank_account_balance = fields.Float()
    is_sick_now = fields.Boolean(compute='_compute_is_sick_now',
        string='Sick Now?')
    sick_ids = fields.One2many('res.partner.sick', 'partner_id',
        string='Sickness')

    @api.multi
    def _compute_is_sick_now(self):
        for this in self:
            sick_line = this.sick_ids.filtered(lambda x: not x.date_end)
            this.is_sick_now = True if sick_line else False

    @api.multi
    def _compute_bank_account_balance(self):
        for this in self:
            journal_ids = this.bank_ids.mapped('journal_id')
            balance = 0.0
            for journal in journal_ids:
                dashboard_datas = journal.get_journal_dashboard_datas()
                balance += dashboard_datas['account_balance']
            this.bank_account_balance = balance

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        if self.bank_account_count <= 0:
            raise ValidationError(_(
                'Error! '
                'You cannot confirm a member that does '
                'not have Bank Account(s).'
            ))

        if self.bank_account_balance <= 0:
            raise ValidationError(_(
                'Error! '
                'You cannot confirm a member that does '
                'not have Bank Balance.'
            ))

        self.state = 'confirmed'

    @api.multi
    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.model
    def cron_amount_balance(self):
        pass
        # TODO: if amount not enough send out mail end month

    @api.model
    def cron_month_member_is_sick(self):
        pass
        # TODO:if yes, create draft payment with button "pay now with bunq"
        # TODO:yes, maybe we send out an email if payment orders generated, but not validated

    @api.model
    def cron_automatic_send_payments(self):
        pass
        # TODO:if validated payout:
        # TODO:send mail to subscription manager: payment sent out
        # TODO:send mail to member: payment received

    # TODO: Add these to res partner
    # send mail when autogenerated invoice
    # contribution_ids field : payments in
    # payment_ids: : payments out
    # contribution_amount field: sum invoices from subscription


class ResPartnerSick(models.Model):
    _name = "res.partner.sick"
    _description = "Sick lines for Members"

    partner_id = fields.Many2one('res.partner')
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
