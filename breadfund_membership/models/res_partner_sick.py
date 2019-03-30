# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class ResPartnerSick(models.Model):
    _name = "res.partner.sick"
    _description = "Sick lines for Members"

    partner_id = fields.Many2one('res.partner')
    name = fields.Char(default='New')
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
    percentage = fields.Float(required=True)
    complete_month = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                    'res.partner.sick') or _('New')
        ret = super(ResPartnerSick, self).create(vals)
        return ret
