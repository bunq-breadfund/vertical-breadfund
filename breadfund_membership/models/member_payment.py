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
    date = fields.Datetime(default=lambda s: fields.Datetime.now())
    amount = fields.Float(required=True)
    sickness_id = fields.Many2many('res.partner.sick')
    state = fields.Selection(STATE, default='draft')

    def action_confirm(self):
        self.ensure_one()
        self.state = 'posted'
