# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


STATE = [
    ('draft', 'Draft'),
    ('confirmed', 'Confirmed')
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection(STATE, default='draft')
    bank_account_balance = fields.Float()
    computed_bank_account_balance = fields.Float(
        compute='_compute_bank_account_balance')
    expected_contribution = fields.Float(
        compute='_compute_expected_contribution')
    total_payment = fields.Float(compute='_compute_total_payment')
    is_sick_now = fields.Boolean(compute='_compute_is_sick_now',
        string='Sick Now?')
    sick_ids = fields.One2many('res.partner.sick', 'partner_id',
        string='Sickness')
    factor = fields.Float(default=1.5)
    monthly_contribution_amount = fields.Float()

    @api.multi
    def _compute_expected_contribution(self):
        for this in self:
            contributions = self.env['member.contribution'].search([
                ('member_from_id', '=', this.id)
            ])
            total = 0.0
            for contribution in contributions:
                total += contribution.amount
            this.expected_contribution = total

    @api.multi
    def _compute_total_payment(self):
        for this in self:
            payments = self.env['member.payment'].search([
                ('member_to_id', '=', this.id)
            ])
            total = 0.0
            for payment in payments:
                total += payment.amount
            this.total_payments = total

    @api.multi
    def _compute_is_sick_now(self):
        for this in self:
            sick_line = this.sick_ids.filtered(lambda x: not x.date_end)
            this.is_sick_now = True if sick_line else False

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

    @api.multi
    def get_active_members(self):
        members = self.search([
            ('state', '=', 'confirmed'),
            ('active', '=', True)
        ])
        return members

    @api.model
    def cron_amount_balance(self):
        members = self.get_active_members()
        # send mail to members (once a month) whose bank balance is
        # less than expected contribution.
        for this in members:
            if this.bank_account_balance < this.expected_contribution:
                template = self.env.ref(
                    'breadfund_membership.mail_template_member_low_bank_balance'
                )
                template.send_mail(this.id)

    @api.multi
    def check_members_can_pay_gift(self, sick):
        ret = True
        percentage = sick.percentage
        factor = 1.5
        members = self.get_active_members()
        total_monthly_contributions = members.mapped(
            'monthly_contribution_amount')
        total_gifts = sum([m.monthly_contribution_amount * factor * percentage for m in members])
        gift_percentage = total_gifts / total_monthly_contributions
        broke_members = members.filtered(
            lambda x:
            x.monthly_contribution_amount * gift_percentage
            >
            x.bank_account_balance
        )
        if broke_members:
            ret = False
            raise UserError(_("some members have insufficient funds!"))
            # TODO: Send mail to admin or the members, show list of members
        return ret

    @api.model
    def cron_month_gift_member(self):
        members = self.get_active_members()
        for member in members:
            # check if days of sickness are a full month
            # check if still sick (no date_end)
            valid_sick = member.sick_ids.filtered(
               lambda x:
                not x.date_end and
                x.complete_month
            )
            if valid_sick:
                members_can_pay = self.check_members_can_pay_gift(valid_sick)
                # create payments if all members can pay gift
                # (to be validated by admin)
                if members_can_pay:
                    for m in members:
                        vals=dict(
                            member_from_id=m.id,
                            member_to_id=member.id,
                            amount=m.monthly_contribution_amount
                        )
                        self.env['member.payment'].create(vals)

        # send mail to admin to validate
        # create payment batch from all payments out (has from and to account)
        # rename payment button to "Pay now with Bunq"

    @api.model
    def cron_automatic_send_payments(self):
        pass
        # TODO:if validated payout:
        # TODO:send mail to subscription manager: payment sent out
        # TODO:send mail to member: payment received

    # TODO: Add these to res partner
    # send mail when autogenerated invoice


class ResPartnerSick(models.Model):
    _name = "res.partner.sick"
    _description = "Sick lines for Members"

    partner_id = fields.Many2one('res.partner')
    name = fields.Char(default='New')
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
    percentage = fields.Float(required=True)
    complete_month = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                    'res.partner.sick') or _('New')
        ret = super(ResPartnerSick, self).create(vals)
        return ret