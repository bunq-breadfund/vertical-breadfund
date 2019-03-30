# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config


class ResCompany(models.Model):
    _inherit = "res.company"

    waiting_days = fields.Integer(
        string='Days of waiting',
        default=14,
        help='The amount of days someone should be sick '
             'before being entitled to sickness money. Note: '
             'payments only arrive another month after this!')
    max_months_sick = fields.Integer(
        string='Max months sick',
        default=24,
        help='Maximum amount of months someone can receive sickness money '
             'through the breadfund.')
