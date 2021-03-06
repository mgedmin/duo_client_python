"""
Duo Security Administration API reference client implementation.

<http://www.duosecurity.com/docs/adminapi>


USERS

User objects are returned in the following format:

        {"username": <str:username>,
         "user_id": <str:user id>,
         "realname": <str:real name>,
         "status": <str:status>,
         "notes": <str:notes>,
         "last_login": <int:unix timestamp>,
         "phones": [<phone object>, ...],
         "tokens": [<token object>, ...]}

User status is one of:

        USER_STATUS_ACTIVE, USER_STATUS_BYPASS, USER_STATUS_DISABLED,
        USER_STATUS_LOCKED_OUT

Note: USER_STATUS_LOCKED_OUT can only be set by the system. You cannot
      set a user to be in the USER_STATUS_LOCKED_OUT state.


PHONES

Phone objects are returned in the following format:

    {"phone_id": <str:phone id>,
     "number": <str:phone number>,
     "extension": <str:phone extension>|'',
     "predelay": <str:predelay in seconds>|None,
     "postdelay": <str:postdelay in seconds>|None,
     "type": <str:phone type>|"Unknown",
     "platform": <str:phone platform>|"Unknown",
     "activated": <bool:is push enabled>,
     "sms_passcodes_sent": <bool:have sms OTP been sent>,
     "users": [<user object>, ...]}


TOKENS

Token objects are returned in the following format:

    {"type": <str:token type>,
     "serial": <str:token serial number>,
     "token_id": <str:token id>,
     "users": [<user object>, ...]}

Token type is one of:

    TOKEN_HOTP_6, TOKEN_HOTP_8, TOKEN_YUBIKEY


SETTINGS

Settings objects are returned in the following format:

    {'inactive_user_expiration': <int:days until expiration>|0,
     'sms_message': <str:sms message>,
     'name': <str:name>,
     'sms_batch': <int:sms batch size>,
     'lockout_threshold': <int:lockout threshold>
     'sms_expiration': <int:minutes until expiration>|0,
     'sms_refresh': <bool:is sms refresh enambed (0|1)>


INTEGRATIONS

Integration objects are returned in the following format:

    {'adminapi_admins': <bool:admins permission (0|1)>,
     'adminapi_info': <bool:info permission (0|1)>,
     'adminapi_integrations': <bool:integrations permission (0|1)>,
     'adminapi_read_log': <bool:read log permission (0|1)>,
     'adminapi_read_resource': <bool:read resource permission (0|1)>,
     'adminapi_settings': <bool:settings permission (0|1)>,
     'adminapi_write_resource': <bool:write resource permission (0|1)>,
     'enroll_policy': <str:enroll policy (enroll|allow|deny)>,
     'greeting': <str:voice greeting>,
     'integration_key': <str:integration key>,
     'name': <str:integration name>,
     'notes': <str:notes>,
     'secret_key': <str:secret key>,
     'type': <str:integration type>,
     'visual_style': <str:visual style>}

See the adminapi docs for possible values for enroll_policy, visual_style,
and type.

ERRORS

Methods will raise a RuntimeError when an error is encountered. When
the call returns a HTTP status other than 200, error will be populated with
the following fields:

    message - String description of the error encountered such as
              "Received 404 Not Found"
    status - HTTP status such as 404 (int)
    reason - Status description such as "Not Found"
    data - Detailed error code such as
           {"code": 40401, "message": "Resource not found", "stat": "FAIL"}
"""

import urllib

import client

USER_STATUS_ACTIVE = 'active'
USER_STATUS_BYPASS = 'bypass'
USER_STATUS_DISABLED = 'disabled'
USER_STATUS_LOCKED_OUT = 'locked out'

TOKEN_HOTP_6 = 'h6'
TOKEN_HOTP_8 = 'h8'
TOKEN_YUBIKEY = 'yk'


class Admin(client.Client):
    account_id = None

    def api_call(self, method, path, params):
        if self.account_id is not None:
            params['account_id'] = self.account_id
        return super(Admin, self).api_call(method, path, params)

    def get_administrator_log(self,
                              mintime=0):
        """
        Returns administrator log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
                  records that have already been fetched)

        Returns:
            [
                {'timestamp': <int:unix timestamp>,
                 'eventtype': "administrator",
                 'host': <str:hostname>,
                 'username': <str:username>,
                 'action': <str:action>,
                 'object': <str:object name>|None,
                 'description': <str:description>|None}, ...
            ]

        <action> is one of:
            'admin_login',
            'admin_create', 'admin_update', 'admin_delete',
            'customer_update',
            'group_create', 'group_update', 'group_delete',
            'integration_create', 'integration_update', 'integration_delete',
            'phone_create', 'phone_update', 'phone_delete',
            'user_create', 'user_update', 'user_delete'

        Raises RuntimeError on error.
        """
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = str(int(mintime))
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/administrator',
            params,
        )
        for row in response:
            row['eventtype'] = 'administrator'
            row['host'] = self.host
        return response


    def get_authentication_log(self,
                               mintime=0):
        """
        Returns authentication log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
                  records that have already been fetched)

        Returns:
            [
                {'timestamp': <int:unix timestamp>,
                 'eventtype': "authentication",
                 'host': <str:host>,
                 'username': <str:username>,
                 'factor': <str:factor>,
                 'result': <str:result>,
                 'ip': <str:ip address>,
                 'integration': <str:integration>}, ...
            ]

        Raises RuntimeError on error.
        """
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = str(int(mintime))
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/authentication',
            params,
        )
        for row in response:
            row['eventtype'] = 'authentication'
            row['host'] = self.host
        return response


    def get_telephony_log(self,
                          mintime=0):
        """
        Returns telephony log events.

        mintime - Fetch events only >= mintime (to avoid duplicate
                  records that have already been fetched)

        Returns:
            [
                {'timestamp': <int:unix timestamp>,
                 'eventtype': "telephony",
                 'host': <str:host>,
                 'context': <str:context>,
                 'type': <str:type>,
                 'phone': <str:phone number>,
                 'credits': <str:credits>}, ...
            ]

        Raises RuntimeError on error.
        """
        # Sanity check mintime as unix timestamp, then transform to string
        mintime = str(int(mintime))
        params = {
            'mintime': mintime,
        }
        response = self.json_api_call(
            'GET',
            '/admin/v1/logs/telephony',
            params,
        )
        for row in response:
            row['eventtype'] = 'telephony'
            row['host'] = self.host
        return response


    def get_users(self):
        """
        Returns list of users.


        Returns list of user objects.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/users', {})
        return response


    def get_user_by_id(self, user_id):
        """
        Returns user specified by user_id.

        user_id - User to fetch

        Returns user object.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        response = self.json_api_call('GET', path, {})
        return response


    def get_users_by_name(self, username):
        """
        Returns user specified by username.

        username - User to fetch

        Returns a list of 0 or 1 user objects.

        Raises RuntimeError on error.
        """
        params = {
            'username': username,
        }
        response = self.json_api_call('GET',
                                      '/admin/v1/users',
                                      params)
        return response


    def add_user(self, username, realname=None, status=None,
                 notes=None):
        """
        Adds a user.

        username - Username
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)

        Returns newly created user object.

        Raises RuntimeError on error.
        """
        params = {
            'username': username,
        }
        if realname is not None:
            params['realname'] = realname
        if status is not None:
            params['status'] = status
        if notes is not None:
            params['notes'] = notes
        response = self.json_api_call('POST',
                                      '/admin/v1/users',
                                      params)
        return response


    def update_user(self, user_id, username=None, realname=None,
                    status=None, notes=None):
        """
        Update username, realname, status, or notes for a user.

        user_id - User ID
        username - Username (optional)
        realname - User's real name (optional)
        status - User's status, defaults to USER_STATUS_ACTIVE
        notes - Comment field (optional)

        Returns updated user object.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        params = {}
        if username is not None:
            params['username'] = username
        if realname is not None:
            params['realname'] = realname
        if status is not None:
            params['status'] = status
        if notes is not None:
            params['notes'] = notes
        response = self.json_api_call('POST', path, params)
        return response


    def delete_user(self, user_id):
        """
        Deletes a user. If the user is already deleted, does nothing.

        user_id - User ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id
        self.json_api_call('DELETE', path, {})


    def get_user_bypass_codes(self, user_id, count=10, valid_secs=0):
        """
        Replace a user's bypass codes with new codes.

        user_id - User ID
        count - Number of new codes to generate
        valid_secs - Seconds before codes expire (if 0 they will never expire)

        Returns a list of newly created codes.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/bypass_codes'
        count = str(int(count))
        valid_secs = str(int(valid_secs))
        params = {
            'count': count,
            'valid_secs': valid_secs,
        }
        return self.json_api_call('POST', path, params)


    def get_user_phones(self, user_id):
        """
        Returns an array of phones associated with the user.

        user_id - User ID

        Returns list of phone objects.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones'
        return self.json_api_call('GET', path, {})


    def add_user_phone(self, user_id, phone_id):
        """
        Associates a phone with a user.

        user_id - User ID
        phone_id - Phone ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones'
        params = {
            'phone_id': phone_id,
        }
        return self.json_api_call('POST', path, params)


    def delete_user_phone(self, user_id, phone_id):
        """
        Dissociates a phone from a user.

        user_id - User ID
        phone_id - Phone ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/phones/' + phone_id
        params = {}
        return self.json_api_call('DELETE', path,
                                    params)


    def get_user_tokens(self, user_id):
        """
        Returns an array of hardware tokens associated with the user.

        user_id - User ID

        Returns list of hardware token objects.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/tokens'
        params = {}
        return self.json_api_call('GET', path,
                                    params)


    def add_user_token(self, user_id, token_id):
        """
        Associates a hardware token with a user.

        user_id - User ID
        token_id - Token ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        path = '/admin/v1/users/' + user_id + '/tokens'
        params = {
            'token_id': token_id,
        }
        return self.json_api_call('POST', path, params)


    def delete_user_token(self, user_id, token_id):
        """
        Dissociates a hardware token from a user.

        user_id - User ID
        token_id - Hardware token ID

        Returns nothing.

        Raises RuntimeError on error.
        """
        user_id = urllib.quote_plus(str(user_id))
        token_id = urllib.quote_plus(str(token_id))
        path = '/admin/v1/users/' + user_id + '/tokens/' + token_id
        return self.json_api_call('DELETE', path, {})


    def get_phones(self):
        """
        Returns list of phones.


        Returns list of phone objects.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/phones', {})
        return response


    def get_phone_by_id(self, phone_id):
        """
        Returns a phone specified by phone_id.

        phone_id - Phone ID

        Returns phone object.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id
        response = self.json_api_call('GET', path, {})
        return response


    def get_phones_by_number(self, number, extension=None):
        """
        Returns a phone specified by number and extension.

        number - Phone number
        extension - Phone number extension (optional)

        Returns list of 0 or 1 phone objects.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones'
        params = {'number': number}
        if extension is not None:
            params['extension'] = extension
        response = self.json_api_call('GET', path,
                                        params)
        return response


    def add_phone(self, number,
                  extension=None,
                  type=None,
                  platform=None,
                  predelay=None,
                  postdelay=None):
        """
        Adds a phone.

        number - Phone number
        extension - Phone number extension (optional)
        type - The phone type.
        platform - The phone platform.
        predelay - Number of seconds to wait after the number picks up
                   before dialing the extension.
        postdelay - Number of seconds to wait after the extension is
                    dialed before the speaking the prompt.

        Returns phone object.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones'
        params = {'number': number}
        if extension is not None:
            params['extension'] = extension
        if type is not None:
            params['type'] = type
        if platform is not None:
            params['platform'] = platform
        if predelay is not None:
            params['predelay'] = predelay
        if postdelay is not None:
            params['postdelay'] = postdelay
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def delete_phone(self, phone_id):
        """
        Deletes a phone. If the phone has already been deleted, does nothing.

        phone_id - Phone ID.

        Returns nothing.

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id
        params = {}
        self.json_api_call('DELETE', path,
                             params)


    def send_sms_activation_to_phone(self, phone_id,
                                     valid_secs=None,
                                     install=None,
                                     installation_msg=None,
                                     activation_msg=None):
        """
        Generate a Duo Mobile activation code and send it to the phone via
        SMS, optionally sending an additional message with a PATH to
        install Duo Mobile.

        phone_id - Phone ID.
        valid_secs - The number of seconds activation code should be valid for.
                     Default: 86400 seconds (one day).
        install - '1' to also send an installation SMS message before the
                  activation message; '0' to not send. Default: '0'.
        installation_msg - Custom installation message template to send to
                           the user if install was 1. Must contain
                           <instpath>, which is replaced with the
                           installation PATH.
        activation_msg - Custom activation message template. Must contain
                         <actpath>, which is replaced with the activation PATH.

        Returns: {
            "activation_msg": "To activate the Duo Mobile app, click this link: https://m-eval.duosecurity.com/iphone/7dmi4Oowz5g3J47FARLs",
            "installation_msg": "Welcome to Duo! To install the Duo Mobile app, click this link: http://m-eval.duosecurity.com",
            "valid_secs": 3600
        }

        Raises RuntimeError on error.
        """
        path = '/admin/v1/phones/' + phone_id + '/send_sms_activation'
        params = {}
        if valid_secs is not None:
            params['valid_secs'] = valid_secs
        if install is not None:
            params['install'] = str(install)
        if installation_msg is not None:
            params['installation_msg'] = installation_msg
        if activation_msg is not None:
            params['activation_msg'] = activation_msg
        return self.json_api_call('POST', path,
                                    params)


    def get_tokens(self):
        """
        Returns list of tokens.


        Returns list of token objects.
        """
        params = {}
        response = self.json_api_call(
            'GET', '/admin/v1/tokens',
            params
        )
        return response


    def get_token_by_id(self, token_id):
        """
        Returns a token.

        token_id - Token ID

        Returns a token object.
        """
        token_id = urllib.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id
        params = {}
        response = self.json_api_call('GET', path,
                                        params)
        return response


    def get_tokens_by_serial(self, type, serial):
        """
        Returns a token.

        type - Token type, one of TOKEN_HOTP_6, TOKEN_HOTP_8, TOKEN_YUBIKEY
        serial - Token serial number

        Returns a list of 0 or 1 token objects.
        """
        params = {
            'type': type,
            'serial': serial,
        }
        response = self.json_api_call('GET', '/admin/v1/tokens', params)
        return response


    def delete_token(self, token_id):
        """
        Deletes a token. If the token is already deleted, does nothing.

        token_id - Token ID

        Returns nothing on success.
        """
        token_id = urllib.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id
        self.json_api_call('DELETE', path, {})


    def add_hotp6_token(self, serial, secret):
        """
        Add a HOTP6 token.

        serial - Token serial number
        secret - HOTP secret

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'h6', 'serial': serial, 'secret': secret}
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_hotp8_token(self, serial, secret):
        """
        Add a HOTP8 token.

        serial - Token serial number
        secret - HOTP secret

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'h8', 'serial': serial, 'secret': secret}
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def add_yubikey_token(self, serial, private_id, aes_key):
        """
        Add a Yubikey AES token.

        serial - Token serial number
        secret - HOTP secret

        Returns newly added token object.
        """
        path = '/admin/v1/tokens'
        params = {'type': 'yk', 'serial': serial, 'private_id': private_id,
                  'aes_key': aes_key}
        response = self.json_api_call('POST', path,
                                        params)
        return response


    def resync_hotp_token(self, token_id, code1, code2, code3):
        """
        Resync HOTP counter. The user must generate 3 consecutive OTP
        from their token and input them as code1, code2, and code3. This
        function will scan ahead in the OTP sequence to find a counter
        that resyncs with those 3 codes.

        token_id - Token ID
        code1 - First OTP from token
        code2 - Second OTP from token
        code3 - Third OTP from token

        Returns nothing on success.
        """
        token_id = urllib.quote_plus(str(token_id))
        path = '/admin/v1/tokens/' + token_id + '/resync'
        params = {'code1': code1, 'code2': code2, 'code3': code3}
        self.json_api_call('POST', path, params)


    def get_settings(self):
        """
        Returns customer settings.


        Returns a settings object.

        Raises RuntimeError on error.
        """

        response = self.json_api_call('GET', '/admin/v1/settings', {})

        return response


    def update_settings(self,
                         lockout_threshold=None,
                        inactive_user_expiration=None,
                        sms_batch=None,
                        sms_expiration=None,
                        sms_refresh=None,
                        sms_message=None,
                        fraud_email=None,
                        keypress_confirm=None,
                        keypress_fraud=None,
                        timezone=None,
                        caller_id=None):
        """
        Update settings.

        lockout_threshold - <int:number of attempts>|None
        inactive_user_expiration - <int:number of days>|None
        sms_batch - <int:batch size>|None
        sms_expiration - <int:minutes>|None
        sms_refresh - True|False|None
        sms_message - <str:message>|None
        fraud_email - <str:email address>|None
        keypress_confirm - <str:0-9, #, or *>|None
        keypress_fraud - <str:0-9, #, or *>|None
        timezone - <str:IANA timezone>|NOne
        caller_id - <str:phone number>

        Returns updated settings object.

        Raises RuntimeError on error.

        """
        params = {}
        if lockout_threshold is not None:
            params['lockout_threshold'] = str(lockout_threshold)
        if inactive_user_expiration is not None:
            params['inactive_user_expiration'] = str(inactive_user_expiration)
        if sms_batch is not None:
            params['sms_batch'] = str(sms_batch)
        if sms_expiration is not None:
            params['sms_expiration'] = str(sms_expiration)
        if sms_refresh is not None:
            params['sms_refresh'] = '1' if sms_refresh else '0'
        if sms_message is not None:
            params['sms_message'] = sms_message
        if fraud_email is not None:
            params['fraud_email'] = fraud_email
        if keypress_confirm is not None:
            params['keypress_confirm'] = keypress_confirm
        if keypress_fraud is not None:
            params['keypress_fraud'] = keypress_fraud
        if timezone is not None:
            params['timezone'] = timezone
        if caller_id is not None:
            params['caller_id'] = caller_id

        if not params:
            raise TypeError("No settings were provided")

        response = self.json_api_call('POST',
                                      '/admin/v1/settings',
                                      params)
        return response


    def get_info_summary(self):
        """
        Returns a summary of objects in the account.


        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/summary',
            params
        )
        return response


    def get_info_telephony_credits_used(self,
                                        mintime=None,
                                        maxtime=None):
        """
        Returns number of telephony credits used during the time period.

        mintime - Limit report to data for events after this UNIX
                  timestamp. Defaults to thirty days ago.
        maxtime - Limit report to data for events before this UNIX
                  timestamp. Defaults to the current time.

        Raises RuntimeError on error.
        """
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/telephony_credits_used',
            params
        )
        return response


    def get_authentication_attempts(self,
                                    mintime=None,
                                    maxtime=None):
        """
        Returns counts of authentication attempts, broken down by result.

        mintime - Limit report to data for events after this UNIX
                  timestamp. Defaults to thirty days ago.
        maxtime - Limit report to data for events before this UNIX
                  timestamp. Defaults to the current time.

        Returns: {
            "ERROR": <int>,
            "FAILURE": <int>,
            "FRAUD": <int>,
            "SUCCESS": <int>
        }

        where each integer is the number of authentication attempts with
        that result.

        Raises RuntimeError on error.
        """
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/authentication_attempts',
            params
        )
        return response


    def get_user_authentication_attempts(self,
                                         mintime=None,
                                         maxtime=None):
        """
        Returns number of unique users with each possible authentication result.

        mintime - Limit report to data for events after this UNIX
                  timestamp. Defaults to thirty days ago.
        maxtime - Limit report to data for events before this UNIX
                  timestamp. Defaults to the current time.

        Returns: {
            "ERROR": <int>,
            "FAILURE": <int>,
            "FRAUD": <int>,
            "SUCCESS": <int>
        }

        where each integer is the number of users who had at least one
        authentication attempt ending with that result. (These counts are
        thus always less than or equal to those returned by
        get_authentication_attempts.)

        Raises RuntimeError on error.
        """
        params = {}
        if mintime is not None:
            params['mintime'] = mintime
        if maxtime is not None:
            params['maxtime'] = maxtime
        response = self.json_api_call(
            'GET',
            '/admin/v1/info/user_authentication_attempts',
            params
        )
        return response


    def get_integrations(self):
        """
        Returns list of integrations.


        Returns list of integration objects.

        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/integrations',
            params
        )
        return response


    def get_integration(self, integration_key):
        """
        Returns the requested integration.

        integration_key - The ikey of the integration to get

        Returns list of integration objects.

        Raises RuntimeError on error.
        """
        params = {}
        response = self.json_api_call(
            'GET',
            '/admin/v1/integrations/' + integration_key,
            params
        )
        return response


    def create_integration(self,
                           name,
                           integration_type,
                           visual_style=None,
                           greeting=None,
                           notes=None,
                           enroll_policy=None,
                           adminapi_admins=None,
                           adminapi_info=None,
                           adminapi_integrations=None,
                           adminapi_read_log=None,
                           adminapi_read_resource=None,
                           adminapi_settings=None,
                           adminapi_write_resource=None):
        """Creates a new integration.

        name - The name of the integration (required)
        integration_type - <str: integration type constant> (required)
                           See adminapi docs for possible values.
        visual_style - <str:visual style constant> (optional, default 'default')
                       See adminapi docs for possible values.
        greeting - <str:Voice greeting> (optional, default '')
        notes - <str:internal use> (optional, uses default setting)
        enroll_policy - <str:'enroll'|'allow'|'deny'> (optional, default 'enroll')
        adminapi_admins - <bool: admins permission>|None
        adminapi_info - <bool: info permission>|None
        adminapi_integrations - <bool:integrations permission>|None
        adminapi_read_log - <bool:read log permission>|None
        adminapi_read_resource - <bool: read resource permission>|None
        adminapi_settings - <bool: settings permission>|None
        adminapi_write_resource - <bool:write resource permission>|None

        Returns the created integration.

        Raises RuntimeError on error.

        """
        params = {}
        if name is not None:
            params['name'] = name
        if integration_type is not None:
            params['type'] = integration_type
        if visual_style is not None:
            params['visual_style'] = visual_style
        if greeting is not None:
            params['greeting'] = greeting
        if notes is not None:
            params['notes'] = notes
        if enroll_policy is not None:
            params['enroll_policy'] = enroll_policy
        if adminapi_admins is not None:
            params['adminapi_admins'] = '1' if adminapi_admins else '0'
        if adminapi_info is not None:
            params['adminapi_info'] = '1' if adminapi_info else '0'
        if adminapi_integrations is not None:
            params['adminapi_integrations'] = '1' if adminapi_integrations else '0'
        if adminapi_read_log is not None:
            params['adminapi_read_log'] = '1' if adminapi_read_log else '0'
        if adminapi_read_resource is not None:
            params['adminapi_read_resource'] = (
                '1' if adminapi_read_resource else '0')
        if adminapi_settings is not None:
            params['adminapi_settings'] = '1' if adminapi_settings else '0'
        if adminapi_write_resource is not None:
            params['adminapi_write_resource'] = (
                '1' if adminapi_write_resource else '0')
        response = self.json_api_call('POST',
                                      '/admin/v1/integrations',
                                      params)
        return response


    def delete_integration(self, integration_key):
        """Deletes an integration.

        integration_key - The integration key of the integration to delete.

        Returns None.

        Raises RuntimeError on error.

        """
        integration_key = urllib.quote_plus(str(integration_key))
        path = '/admin/v1/integrations/%s' % integration_key
        self.json_api_call('DELETE', path, {})
        return None


    def update_integration(self,
                           integration_key,
                           name=None,
                           visual_style=None,
                           greeting=None,
                           notes=None,
                           enroll_policy=None,
                           adminapi_admins=None,
                           adminapi_info=None,
                           adminapi_integrations=None,
                           adminapi_read_log=None,
                           adminapi_read_resource=None,
                           adminapi_settings=None,
                           adminapi_write_resource=None,
                           reset_secret_key=None):
        """Updates an integration.

        integration_key - The key of the integration to update. (required)
        name - The name of the integration (optional)
        visual_style - (optional, default 'default')
                       See adminapi docs for possible values.
        greeting - Voice greeting (optional, default '')
        notes - internal use (optional, uses default setting)
        enroll_policy - <'enroll'|'allow'|'deny'> (optional, default 'enroll')
        adminapi_admins - <int:0|1>|None
        adminapi_info - True|False|None
        adminapi_integrations - True|False|None
        adminapi_read_log - True|False|None
        adminapi_read_resource - True|False|None
        adminapi_settings - True|False|None
        adminapi_write_resource - True|False|None
        reset_secret_key - <any value>|None

        If any value other than None is provided for 'reset_secret_key'
        (for example, 1), then a new secret key will be generated for the
        integration.

        Returns the created integration.

        Raises RuntimeError on error.

        """
        integration_key = urllib.quote_plus(str(integration_key))
        path = '/admin/v1/integrations/%s' % integration_key
        params = {}
        if name is not None:
            params['name'] = name
        if visual_style is not None:
            params['visual_style'] = visual_style
        if greeting is not None:
            params['greeting'] = greeting
        if notes is not None:
            params['notes'] = notes
        if enroll_policy is not None:
            params['enroll_policy'] = enroll_policy
        if adminapi_admins is not None:
            params['adminapi_admins'] = '1' if adminapi_admins else '0'
        if adminapi_info is not None:
            params['adminapi_info'] = '1' if adminapi_info else '0'
        if adminapi_integrations is not None:
            params['adminapi_integrations'] = '1' if adminapi_integrations else '0'
        if adminapi_read_log is not None:
            params['adminapi_read_log'] = '1' if adminapi_read_log else '0'
        if adminapi_read_resource is not None:
            params['adminapi_read_resource'] = (
                '1' if adminapi_read_resource else '0')
        if adminapi_settings is not None:
            params['adminapi_settings'] = '1' if adminapi_settings else '0'
        if adminapi_write_resource is not None:
            params['adminapi_write_resource'] = (
                '1' if adminapi_write_resource else '0')
        if reset_secret_key is not None:
            params['reset_secret_key'] = '1'

        if not params:
            raise TypeError("No new values were provided")

        response = self.json_api_call('POST', path, params)
        return response


    def get_admins(self):
        """
        Returns list of administrators.


        Returns list of administrator objects.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        response = self.json_api_call('GET', '/admin/v1/admins', {})
        return response


    def get_admin(self, admin_id):
        """
        Returns an administrator.

        admin_id - The id of the administrator.

        Returns an administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = urllib.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        response = self.json_api_call('GET', path, {})
        return response


    def add_admin(self, name, email, phone, password):
        """
        Create an administrator and adds it to a customer.

        name - <str:the name of the administrator>
        email - <str:email address>
        phone - <str:phone number>
        password - <str:pasword>

        Returns the added administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        params = {}
        if name is not None:
            params['name'] = name
        if email is not None:
            params['email'] = email
        if phone is not None:
            params['phone'] = phone
        if password is not None:
            params['password'] = phone
        response = self.json_api_call('POST', '/admin/v1/admins', params)
        return response


    def update_admin(self, admin_id,
                     name=None,
                     phone=None,
                     password=None):
        """
        Create an administrator and adds it to a customer.

        admin_id - The id of the administrator.
        name - <str:the name of the administrator> (optional)
        phone - <str:phone number> (optional)
        password - <str:password> (optional)

        Returns the updated administrator.  See the adminapi docs.

        Raises RuntimeError on error.
        """
        admin_id = urllib.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        params = {}
        if name is not None:
            params['name'] = name
        if phone is not None:
            params['phone'] = phone
        if password is not None:
            params['password'] = password
        response = self.json_api_call('POST', path, params)
        return response


    def delete_admin(self, admin_id):
        """
        Deletes an administrator.

        admin_id - The id of the administrator.

        Returns None.

        Raises RuntimeError on error.
        """
        admin_id = urllib.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s' % admin_id
        self.json_api_call('DELETE', path, {})


    def reset_admin(self, admin_id):
        """
        Resets the admin lockout.

        admin_id - <int:admin id>

        Returns None.

        Raises RuntimeError on error.
        """
        admin_id = urllib.quote_plus(str(admin_id))
        path = '/admin/v1/admins/%s/reset' % admin_id
        self.json_api_call('POST', path, {})


    def activate_admin(self, email,
                       send_email=False,
                       valid_days=None):
        """
        Generates an activate code for an administrator and optionally
        emails the administrator.

        email - <str:email address of administrator>
        valid_days - <int:number of days> (optional)
        send_email - <bool: True if email should be sent> (optional)

        Returns {
            "email": <str:email for admin/message>,
            "valid_days": <int:valid days>
            "link": <str:activation link>
            "message": <str:message, whether sent or not>
            "email_sent": <bool:true if email was sent, false otherwise>
            "code": <str:activation code>
        }

        See the adminapi docs for updated return values.

        Raises RuntimeError on error.
        """
        params = {}
        if email is not None:
            params['email'] = email
        if send_email is not None:
            params['send_email'] = '1' if send_email else '0'
        if valid_days is not None:
            params['valid_days'] = str(valid_days)
        response = self.json_api_call('POST',
                                      '/admin/v1/admins/activate',
                                      params)
        return response

    def get_logo(self):
        """
        Returns current logo's PNG data or raises an error if none is set.

        Raises RuntimeError on error.
        """
        response, data = self.api_call('GET',
                                       '/admin/v1/logo',
                                       params={})
        content_type = response.getheader('Content-Type')
        if content_type and content_type.startswith('image/'):
            return data
        else:
            return self.parse_json_response(response, data)

    def update_logo(self, logo):
        """
        Set a logo that will appear in future Duo Mobile activations.

        logo - <str:PNG byte sequence>

        Raises RuntimeError on error.
        """
        params = {
            'logo': logo.encode('base64'),
        }
        self.json_api_call('POST',
                           '/admin/v1/logo',
                           params)

    def delete_logo(self):
        self.json_api_call('DELETE',
                           '/admin/v1/logo',
                           params={})
