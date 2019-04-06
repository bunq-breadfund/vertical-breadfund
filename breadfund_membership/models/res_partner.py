# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError


STATE = [
    ('draft', 'Draft'),
    ('waiting_auth', 'Awaiting authorization'),
    ('active', 'Active'),
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    state = fields.Selection(STATE, default='draft')
    bank_account_balance = fields.Monetary(
        string='Account balance')
    computed_bank_account_balance = fields.Monetary(
        string='Account balance',
        compute='_compute_bank_account_balance')
    expected_contribution = fields.Monetary(
        compute='_compute_expected_contribution')
    total_payment = fields.Monetary(compute='_compute_total_payment')
    is_sick_now = fields.Boolean(compute='_compute_is_sick_now',
        string='Sick Now?')
    sick_ids = fields.One2many(
        'res.partner.sick', 'partner_id',
        string='Sickness')
    monthly_contribution_amount = fields.Monetary(
        string='Monthly contribution',
        related='member_type_id.monthly_contribution_amount',
        readonly=True)
    monthly_sick_amount = fields.Monetary(
        string='Amount received when sick',
        related='member_type_id.monthly_sick_amount',
        readonly=True)
    member_type_id = fields.Many2one(
        'res.partner.member.type',
        default=lambda self: self.env.ref(
            'breadfund_membership.basic_member_type',
            raise_if_not_found=False)
            or self.env['res.partner.member.type'].browse([]),
        string="Member Type")
    calculated_savings = fields.Monetary(
        compute='_compute_calculated_savings',
        store=True)
    fair_share_factor = fields.Float(
        string='Fair share factor',
        compute='_compute_fair_share_factor'
    )

    def _compute_fair_share_factor(self):
        total_amount = 0.0
        self.env.cr.execute('''
            select sum(t.monthly_sick_amount)
            from res_partner p, res_partner_member_type t
            where p.member_type_id = t.id
            and p.state = 'active'
        ''')
        result = self.env.cr.fetchall()
        if result:
            total_amount = result[0][0]
        for this in self:
            if total_amount > 0:
                this.fair_share_factor = \
                    this.monthly_sick_amount / total_amount
            else:
                this.fair_share_factor = 0.0

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
    def action_confirm_details(self):
        self.ensure_one()
        if self.bank_account_count <= 0:
            raise ValidationError(_(
                'You cannot confirm a member that does '
                'not have a bank account.'
            ))
        self.state = 'waiting_auth'

    @api.multi
    def action_confirm_authorization(self):
        self.ensure_one()
        upfront_contrib = self.member_type_id.upfront_contribution_amount
        if self.bank_account_balance < upfront_contrib:
            raise ValidationError(_(
                'To activate a member, the member needs at least %.2f '
                'of bank balance. There is now only %.2f.') % (
                    upfront_contrib,
                    self.bank_account_balance
                )
            )
        self.state = 'active'

    @api.multi
    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.model
    def get_active_members(self):
        return self.search([('state', '=', 'active')])

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

    @api.model
    def cron_daily_gift_member(self):
        today = fields.Date.context_today(self)
        members = self.get_active_members()
        for sickness in members.mapped('sick_ids'):
            next_payment_date = sickness.next_payment_date
            if not next_payment_date or next_payment_date < today:
                continue
            total_gift = sickness.next_payment_amount
            for member in members:
                amount = total_gift * member.fair_share_factor
                if member.bank_account_balance < amount:
                    raise UserError(_(
                        "Member {} only has {}, not {}").format(
                            member.display_name,
                            member.bank_account_balance,
                            amount
                        ))
                vals=dict(
                    partner_from_id=member.id,
                    partner_to_id=sickness.partner_id.id,
                    amount=total_gift * member.fair_share_factor
                )
                self.env['member.payment'].create(vals)
            sickness.payments_made += 1
            # send mail to admin to validate these draft payments

        # create payment batch from all payments out (has from and to account)
        # rename payment button to "Pay now with Bunq"

    @api.model
    def cron_automatic_send_payments(self):
        pass
        # pay out any payments that were validated by admin
        # send mail to subscription manager: payment sent out
        # send mail to member: payment received

    # TODO: Add these to res partner
    # send mail when autogenerated invoice
