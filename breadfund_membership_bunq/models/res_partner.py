# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import config

from ..bunq_lib import BunqLib
from bunq.sdk.context import ApiEnvironmentType


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def update_all_bunq_balances(self):
        for this in self.search([]):
            for bank in this.bank_ids:
                if bank.bank_id.name == 'BUNQ':
                    balance = this._get_bunq_balance(bank.acc_number)
                    this.sudo().write(dict(bank_account_balance=balance))

    @api.model
    def _get_bunq_balance(self, acc_number):
        api_key = config.get('bunq_api_key')
        bunq = BunqLib(ApiEnvironmentType.SANDBOX, api_key=api_key)

        # vind IBAN
        all_monetary_account_bank_active = bunq.get_all_monetary_account_active(1)
        for account in all_monetary_account_bank_active:
            for alias in account.alias:
                if alias.type_ == 'IBAN' and alias.value == acc_number:
                    return account._balance.value
        else:
            print('IBAN niet gevonden')
            return(None)
