# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartnerMemberType(models.Model):
    _name = "res.partner.member.type"

    name = fields.Char()
    partner_id = fields.Many2one('res.partner')
    upfront_contribution_amount = fields.Float(required=True)
    monthly_contribution_amount = fields.Float(required=True)
    monthly_sick_amount = fields.Float(required=True)
