# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
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
                raise ValidationError(
                    'Source and destination members cannot have the same IBAN')
            this._pay_with_bunq(iban_from, iban_to, this.amount)
            this.state = 'paid'

    @api.model
    def _pay_with_bunq(self, iban_from, iban_to, amount):

        def find_type(account,type):
            for alias in account._alias:
                if alias._type_==type:
                    return(alias.value)
            else:
                return(None)

        api_key = config.get('bunq_api_key')
        bunq = BunqLib(ApiEnvironmentType.SANDBOX, api_key=api_key)

        id_from=None
        email_to=None

        # vind IBAN
        all_monetary_account_bank_active = bunq.get_all_monetary_account_active(1)
        for account in all_monetary_account_bank_active:
            if find_type(account, 'IBAN') == iban_from:
                id_from=account.id_
            if find_type(account, 'IBAN') == iban_to:
                email_to_bu=find_type(account,'EMAIL')
                if email_to_bu!=None:
                        email_to=email_to_bu
        if id_from==None or email_to==None:
            print('IBAN niet gevonden')
            return(None)
        else:
            # geld overmaken
            bunq.make_payment(amount, 'test met IBAN', email_to, id_from)
