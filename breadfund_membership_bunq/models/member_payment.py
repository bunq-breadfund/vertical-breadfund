# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

from ..bunq_lib import BunqLib
from bunq.sdk.context import ApiEnvironmentType


class MemberPayment(models.Model):
    _inherit = "member.payment"

    @api.multi
    def pay_with_bunq(self):
        for this in self:
            iban_from = None
            iban_to = None
            for bank in this.partner_from_id.bank_ids:
                if bank.bank_id.name == 'BUNQ':
                    iban_from = bank.acc_number
            for bank in this.partner_to_id.bank_ids:
                if bank.bank_id.name == 'BUNQ':
                    iban_to = bank.acc_number
            if not iban_to or not iban_from:
                raise ValidationError(
                    'Source and destination members should have valid BUNQ accounts')
            if iban_to == iban_from:
                this.state = 'paid'
                continue
            bunq = this.partner_from_id.company_id.make_bunq_connection()
            this._pay_with_bunq(bunq, iban_from, iban_to, this.amount)
            this.state = 'paid'

    @api.model
    def _pay_with_bunq(self, bunq, iban_from, iban_to, amount):

        def find_type(account, _type):
            for alias in account._alias:
                if alias._type_ == _type:
                    return(alias.value)
            else:
                return(None)

        id_from = None
        email_to = None
        all_monetary_account_bank_active = bunq.get_all_monetary_account_active(1)
        for account in all_monetary_account_bank_active:
            if find_type(account, 'IBAN') == iban_from:
                id_from = account.id_
            if find_type(account, 'IBAN') == iban_to:
                email_to = find_type(account, 'EMAIL')
        if not email_to:
            raise UserError(_(
                'No access to destination account: {}').format(
                    iban_to))
        if not id_from:
            raise UserError(_(
                'No access to source account: {}').format(iban_from))
        bunq.make_payment(amount, 'Sickness payment', email_to, id_from)
