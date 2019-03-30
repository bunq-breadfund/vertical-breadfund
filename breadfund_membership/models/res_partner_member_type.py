# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartnerMemberType(models.Model):
    _name = "res.partner.member.type"

    name = fields.Char(required=True)
    partner_ids = fields.One2many('res.partner', 'member_type_id')
    upfront_contribution_amount = fields.Float(
        string='Upfront contribution', required=True)
    monthly_contribution_amount = fields.Float(
        string='Monthly contribution', required=True)
    monthly_sick_amount = fields.Float(
        string='Amount received when sick', required=True)
