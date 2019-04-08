# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

from ..bunq_lib import BunqLib
from bunq.sdk.context import ApiEnvironmentType


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def update_bunq_balance(self):
        self.ensure_one()
        bunq = self.company_id.make_bunq_connection()
        self.company_id.accept_all_requests(bunq)
        self._update_bunq_balance(bunq)

    @api.multi
    def _update_bunq_balance(self, bunq):
        for this in self:
            if not this.bank_ids:
                raise UserError(
                    _('User {} should have a bank account defined').format(
                        this.name))
            if len(this.bank_ids) > 1:
                raise UserError(
                    _('User {} has more than one bank account defined').format(
                        this.name))
            account = this.bank_ids
            bank = account.bank_id
            if bank.name != 'BUNQ':
                raise UserError(
                    _('Account {} is not a BUNQ account!').format(
                        account.acc_number))
            balance = this.get_bunq_balance(bunq, account.acc_number)
            this.write(dict(bank_account_balance=balance))

    @api.multi
    def get_bunq_balance(self, bunq, acc_number):
        all_monetary_account_bank_active = bunq.get_all_monetary_account_active(1)
        for account in all_monetary_account_bank_active:
            for alias in account.alias:
                if alias.type_ == 'IBAN' and alias.value == acc_number:
                    return account._balance.value
        else:
            raise UserError(
                _('No access to bank account {}. Please let user send a '
                  'Bunq Connect request to {}').format(
                    acc_number, self.company_id.bunq_email))
