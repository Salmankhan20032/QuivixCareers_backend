# users/utils.py

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import os  # Import os to check environment variables

# --- Complete and robust implementation for sending OTP emails ---


def send_otp_email(user, otp_code):
    """
    Sends a transactional email containing the OTP to the user.
    """
    # 1. Robustness Check: Ensure the API key is configured.
    #    This prevents a 500 server error if the key is missing in production.
    if not settings.BREVO_API_KEY:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! WARNING: BREVO_API_KEY is not set. Email not sent. !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return

    # 2. Configure the Brevo API client
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = settings.BREVO_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    # 3. Define email properties
    sender = {"name": "QuivixCareers", "email": "noreply@quivixcareers.com"}
    to = [{"email": user.email, "name": user.full_name}]

    # 4. Create the email content (you can use a template or simple HTML)
    html_content = f"""
    <html>
    <body>
        <h2>Hello {user.full_name},</h2>
        <p>Thank you for registering with QuivixCareers. Please use the following One-Time Password (OTP) to verify your account:</p>
        <h1 style="font-size: 2.5em; letter-spacing: 5px; margin: 20px 0; color: #007bff;">{otp_code}</h1>
        <p>This code is valid for 10 minutes. If you did not request this, please ignore this email.</p>
        <br>
        <p>Best Regards,</p>
        <p>The QuivixCareers Team</p>
    </body>
    </html>
    """

    email_to_send = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        sender=sender,
        subject="Your QuivixCareers Verification Code",
        html_content=html_content,
    )

    # 5. Send the email and handle potential errors gracefully
    try:
        api_response = api_instance.send_transac_email(email_to_send)
        print("OTP Email sent successfully. Response: ", api_response)
    except ApiException as e:
        # This ensures your app does NOT crash if the email fails.
        # It will print the error to your server logs for debugging.
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"!!! Brevo API Exception when calling send_transac_email: {e} !!!")
        print(f"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
