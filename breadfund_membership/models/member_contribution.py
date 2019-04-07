# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MemberContribution(models.Model):
    _name = "member.contribution"

    partner_id = fields.Many2one('res.partner', 'Member', required=True)
    name = fields.Char()
    date = fields.Datetime(default=lambda s: fields.Datetime.now())
    amount = fields.Float(required=True)

    @api.model
    def create(self, vals):
        partner_name = self.env['res.partner'].browse(vals['partner_id']).name
        date = fields.Date.from_string(vals['date']).isoformat()
        vals['name'] = "%s - %s - %s" % (
            partner_name, date, vals['amount']
        )
        ret = super(MemberContribution, self).create(vals)
        return ret
