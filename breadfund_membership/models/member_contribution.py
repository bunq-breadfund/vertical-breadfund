# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

STATE = [
    ('draft', 'Draft'),
    ('posted', 'Posted')
]


class MemberContribution(models.Model):
    _name = "member.contribution"

    partner_id = fields.Many2one('res.partner', 'Member', required=True)
    date = fields.Datetime(default=lambda s: fields.Datetime.now())
    amount = fields.Float(required=True)
    state = fields.Selection(STATE, default='draft')