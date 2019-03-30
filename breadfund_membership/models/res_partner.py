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
    bank_account_balance = fields.Float(
        string='Account balance')
    computed_bank_account_balance = fields.Float(
        string='Account balance',
        compute='_compute_bank_account_balance')
    expected_contribution = fields.Float(
        compute='_compute_expected_contribution')
    total_payment = fields.Float(compute='_compute_total_payment')
    is_sick_now = fields.Boolean(compute='_compute_is_sick_now',
        string='Sick Now?')
    sick_ids = fields.One2many('res.partner.sick', 'partner_id',
        string='Sickness')
    monthly_contribution_amount = fields.Float(
        string='Monthly contribution')
    member_type_id = fields.Many2one('res.partner.member.type', required=True,
        string="Member Type")
    calculated_savings = fields.Float(compute='_compute_calculated_savings',
        store=True)

    @api.multi
    def _compute_calculated_savings(self):
        # starting date of membership + upfront contributions +
        # monthly contributions sum - sickness gifts sum
        for this in self:
            upfront_contrib = this.member_type_id.upfront_contribution_amount
            contributions = self.env['member.contribution'].search([
                ('partner_id', '=', this.id),
                ('state', '=', 'posted')
            ]).mapped('amount')
            gifted_payments = self.env['member.payment'].search([
                ('partner_to_id', '=', this.id),
                ('state', '=', 'paid')
            ]).mapped('amount')
            this.calculated_savings = upfront_contrib + sum(contributions) \
                - sum(gifted_payments)

    @api.multi
    def _compute_expected_contribution(self):
        for this in self:
            contributions = self.env['member.contribution'].search([
                ('partner_id', '=', this.id)
            ])
            total = 0.0
            for contribution in contributions:
                total += contribution.amount
            this.expected_contribution = total

    @api.multi
    def _compute_total_payment(self):
        for this in self:
            payments = self.env['member.payment'].search([
                ('partner_to_id', '=', this.id)
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
        members = self.get_active_members()
        factor = 0.5 * len(members)
        total_monthly_contributions = members.mapped(
            'monthly_contribution_amount')
        total_gifts = sum([
            m.monthly_contribution_amount * factor * percentage
            for m in members
        ])
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
    def cron_daily_gift_member(self):
        members = self.get_active_members()
        valid_pay_sickness = False
        for member in members:
            # check if days of sickness are a full month
            # check if still sick (no date_end)
            valid_sick = member.sick_ids.filtered(
               lambda x:
                not x.date_end and
                x.complete_month
            )
            # check date difference in days
            if valid_sick:
                sickness = valid_sick[0]
                today = fields.Datetime.now()
                days_diff = (fields.Date.from_string(sickness.date_start) -
                        fields.Date.from_string(today)).days

            #  if sick since 14 days + one month then valid
            if days_diff > 30 + 14:
                valid_pay_sickness = True

            if days_diff > 14 and \
                sickness.end_date and \
                today > sickness.end_date \
                and today - sickness.start_date < (30 + 14):
                valid_pay_sickness = True

            if valid_pay_sickness:
                members_can_pay = self.check_members_can_pay_gift(valid_sick)
                # create payments if all members can pay gift
                # (to be validated by admin)
                if members_can_pay:
                    for m in members:
                        vals=dict(
                            partner_from_id=m.id,
                            partner_to_id=member.id,
                            amount=m.monthly_contribution_amount
                        )
                        self.env['member.payment'].create(vals)
                        # send mail to admin to validate
                # send mail to admin to validate
                else:
                    pass

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
