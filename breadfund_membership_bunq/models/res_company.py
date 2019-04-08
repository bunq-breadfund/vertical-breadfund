# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

from ..bunq_lib import BunqLib
from bunq.sdk.context import ApiEnvironmentType
from bunq.sdk.exception import BadRequestException


class ResCompany(models.Model):
    _inherit = "res.company"

    bunq_phone = fields.Char(
        string='bunq phone number',
        help='Phone number of the bunq account of the breadfund administrator')
    bunq_email = fields.Char(
        string='bunq email',
        help='Email address to which the bunq account of the breadfund '
             'administrator is registered')
    bunq_api_key = fields.Char(
        string='bunq API key',
        help='API key of the bunq account of the breadfund administrator')

    @api.multi
    def generate_new_sandbox_user(self):
        self.ensure_one()
        bunq = BunqLib(ApiEnvironmentType.SANDBOX)
        user = bunq.get_current_user()
        self.bunq_phone = user._alias[0].value
        self.bunq_email = user._alias[1].value
        self.bunq_api_key = bunq.get_api_key()

    @api.multi
    def make_bunq_connection(self):
        self.ensure_one()
        try:
            return BunqLib(ApiEnvironmentType.SANDBOX, api_key=self.bunq_api_key)
        except BadRequestException as e:
            raise UserError(e)

    @api.model
    def accept_all_requests(self, bunq):
        """ Accept any Bunq Connect requests of people """
        for response in bunq.get_all_share_invite_bank_response():
            bunq.accept_share_invite_bank_response(response._id_)

    @api.model
    def update_all_bunq_balances(self):
        for company in self.search([]):
            bunq = company.make_bunq_connection()
            company.accept_all_requests(bunq)
            members = self.env['res.partner'].search([
                ('state', '=', 'active'),
                ('company_id', '=', company.id),
            ])
            members._update_bunq_balance(bunq)
