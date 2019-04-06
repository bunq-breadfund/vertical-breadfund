# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartnerMemberType(models.Model):
    _name = "res.partner.member.type"

    company_id = fields.Many2one(
        'res.company', string='Company', readonly=True,
        default=lambda self: self.env.user.company_id)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id',
        string='Company Currency', readonly=True)
    name = fields.Char(required=True)
    partner_ids = fields.One2many('res.partner', 'member_type_id')
    upfront_contribution_amount = fields.Monetary(
        string='Upfront contribution', required=True)
    monthly_contribution_amount = fields.Monetary(
        string='Monthly contribution', required=True)
    monthly_sick_amount = fields.Monetary(
        string='Amount received when sick', required=True)
