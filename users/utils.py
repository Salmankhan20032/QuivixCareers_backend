# users/utils.py (NEW FILE)

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import random


def send_otp_email(user, otp_code):
    configuration = sib
