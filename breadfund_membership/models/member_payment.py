# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATE = [
    ('draft', 'Draft'),
    ('posted', 'Posted')
]


class MemberPayment(models.Model):
    _name = "member.payment"

    member_from_id = fields.Many2one('res.partner', 'Member From',
        required=True)
    member_to_id = fields.Many2one('res.partner', 'Member To',
        required=True)
    date = fields.Datetime(default=lambda s: fields.Datetime.now())
    amount = fields.Float(required=True)
    state = fields.Selection(STATE, default='draft')