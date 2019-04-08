# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATE = [
    ('draft', 'Draft'),
    ('posted', 'Posted'),
    ('paid', 'Paid')
]


class MemberPayment(models.Model):
    _name = "member.payment"

    partner_from_id = fields.Many2one('res.partner', 'Member from', required=True)
    partner_to_id = fields.Many2one('res.partner', 'Member to', required=True)
    date = fields.Date(default=lambda self: fields.Date.context_today(self))
    amount = fields.Float(required=True)
    sickness_id = fields.Many2one('res.partner.sick')
    state = fields.Selection(STATE, default='draft')

    @api.multi
    def action_set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    @api.multi
    def name_get(self):
        res = []
        for payment in self:
            name = "{} - {} - {}".format(
                payment.partner_from_id.name,
                fields.Date.from_string(payment.date).isoformat(),
                payment.amount
            )
            res.append((payment.id, name))
        return res

    def action_confirm(self):
        self.ensure_one()
        self.state = 'posted'
