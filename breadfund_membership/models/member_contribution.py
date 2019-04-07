# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MemberContribution(models.Model):
    _name = "member.contribution"

    partner_id = fields.Many2one('res.partner', 'Member', required=True)
    name = fields.Char()
    date = fields.Datetime(default=lambda s: fields.Datetime.now())
    amount = fields.Float(required=True)

    @api.multi
    def name_get(self):
        res = []
        for contribution in self:
            name = "%s - %s - %s" % (
                contribution.partner_id.name,
                fields.Date.from_string(contribution.date).isoformat(),
                contribution.amount
            )
            res.append((contribution.id, name))
        return res
