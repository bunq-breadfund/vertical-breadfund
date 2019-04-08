import json
from os.path import isfile
import socket

import requests
from bunq.sdk.client import Pagination
from bunq.sdk.context import ApiContext
from bunq.sdk.context import ApiEnvironmentType
from bunq.sdk.context import BunqContext
from bunq.sdk.exception import BunqException
from bunq.sdk.model.generated import endpoint
from bunq.sdk.model.generated.object_ import Pointer, Amount, NotificationFilter

NOTIFICATION_DELIVERY_METHOD_URL = 'URL'

NOTIFICATION_CATEGORY_MUTATION = 'MUTATION'


class BunqLib(object):
    _ERROR_COULD_NOT_DETIRMINE_CONF = 'Could not find the bunq configuration' \
                                      ' file.'

    _MONETARY_ACCOUNT_STATUS_ACTIVE = 'ACTIVE'

    _DEFAULT_COUNT = 10
    _POINTER_TYPE_EMAIL = 'EMAIL'
    _CURRENCY_EURL = 'EUR'
    _DEVICE_DESCRIPTION = "python tinker"

    def __init__(self, env, api_key=None):
        """
        :type env: ApiEnvironmentType
        """

        self.user = None
        self.env = env
        if not api_key:
            result = self.generate_new_sandbox_user()
            api_key = result.api_key
        self.api_key = api_key
        self.setup_context(api_key)
        self.setup_current_user()

    def setup_context(self, api_key):
        api_context = ApiContext(
            ApiEnvironmentType.SANDBOX,
            api_key,
            socket.gethostname()
        )
        api_context.ensure_session_active()
        BunqContext.load_api_context(api_context)

    def setup_current_user(self):
        user = endpoint.User.get().value.get_referenced_object()
        if (isinstance(user, endpoint.UserPerson)
                or isinstance(user, endpoint.UserCompany)
                or isinstance(user, endpoint.UserLight)
        ):
            self.user = user

    def get_api_key(self):
        """
        :rtype: string
        """

        return self.api_key

    def get_current_user(self):
        """
        :rtype: UserCompany|UserPerson
        """

        return self.user

    def get_all_monetary_account_active(self, count=_DEFAULT_COUNT):
        """
        :type count: int
        :rtype: list[endpoint.MonetaryAccountBank]
        """

        pagination = Pagination()
        pagination.count = count

        all_monetary_account_bank = endpoint.MonetaryAccountBank.list(
            pagination.url_params_count_only).value
        all_monetary_account_bank_active = []

        for monetary_account_bank in all_monetary_account_bank:
            if monetary_account_bank.status == \
                    self._MONETARY_ACCOUNT_STATUS_ACTIVE:
                all_monetary_account_bank_active.append(monetary_account_bank)

        return all_monetary_account_bank_active

    def get_all_share_invite_bank_response(self, count=_DEFAULT_COUNT):
        """
        :type count: int
        :rtype: list[endpoint.ShareInviteBankResponse]
        """

        pagination = Pagination()
        pagination.count = count

        all_share_invite_bank_response = endpoint.ShareInviteBankResponse.list(
            pagination.url_params_count_only).value
        return all_share_invite_bank_response

    def accept_share_invite_bank_response(self, _id):
        endpoint.ShareInviteBankResponse.update(
            share_invite_bank_response_id=_id,
            status='ACCEPTED')

    def get_all_payment(self, count=_DEFAULT_COUNT):
        """
        :type count: int
        :rtype: list[Payment]
        """

        pagination = Pagination()
        pagination.count = count

        return endpoint.Payment.list(
            params=pagination.url_params_count_only).value

    def get_all_request(self, count=_DEFAULT_COUNT):
        """
        :type count: int
        :rtype: list[endpoint.RequestInquiry]
        """

        pagination = Pagination()
        pagination.count = count

        return endpoint.RequestInquiry.list(
            params=pagination.url_params_count_only).value

    def make_payment(self, amount_string, description, recipient, account_id):
        """
        :type amount_string: str
        :type description: str
        :type recipient: str
        """

        endpoint.Payment.create(
            amount=Amount(amount_string, self._CURRENCY_EURL),
            counterparty_alias=Pointer(self._POINTER_TYPE_EMAIL, recipient),
            description=description,
            monetary_account_id=account_id
        )

    def make_request(self, amount_string, description, recipient):
        """
        :type amount_string: str
        :type description: str
        :type recipient: str
        """

        endpoint.RequestInquiry.create(
            amount_inquired=Amount(amount_string, self._CURRENCY_EURL),
            counterparty_alias=Pointer(self._POINTER_TYPE_EMAIL, recipient),
            description=description,
            allow_bunqme=True
        )

    def get_all_user_alias(self):
        """
        :rtype: list[Pointer]
        """

        return self.get_current_user().alias

    def generate_new_sandbox_user(self):
        """
        :rtype: SandboxUser
        """

        url = "https://public-api.sandbox.bunq.com/v1/sandbox-user"

        headers = {
            'x-bunq-client-request-id': "uniqueness-is-required",
            'cache-control': "no-cache",
            'x-bunq-geolocation': "0 0 0 0 NL",
            'x-bunq-language': "en_US",
            'x-bunq-region': "en_US",
        }

        response = requests.request("POST", url, headers=headers)

        if response.status_code is 200:
            response_json = json.loads(response.text)
            return endpoint.SandboxUser.from_json(
                json.dumps(response_json["Response"][0]["ApiKey"]))

        raise BunqException(self._ERROR_COULD_NOT_CREATE_NEW_SANDBOX_USER)
