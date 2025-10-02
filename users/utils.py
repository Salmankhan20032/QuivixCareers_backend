# users/utils.py

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from django.conf import settings
import os

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
    #    --- THIS IS THE CRUCIAL LINE WE UPDATED ---
    #    It now uses your verified professional email sender.
    sender = {"name": "QuivixCareers", "email": "noreply@quivixdigital.com"}
    to = [{"email": user.email, "name": user.full_name}]

    # 4. Create the email content using a clean and simple HTML template
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Verification Code</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
            .header {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .otp-code {{ font-size: 36px; font-weight: bold; letter-spacing: 5px; margin: 25px 0; padding: 10px; text-align: center; background-color: #f8f9fa; border-radius: 5px; }}
            .footer {{ font-size: 12px; color: #777; margin-top: 20px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <p class="header">Hello {user.full_name},</p>
            <p>Thank you for registering with QuivixCareers. Please use the following One-Time Password (OTP) to verify your account:</p>
            <div class="otp-code">{otp_code}</div>
            <p>This code is valid for 10 minutes. If you did not request this, please ignore this email.</p>
            <br>
            <p>Best Regards,</p>
            <p>The QuivixCareers Team</p>
            <div class="footer">
                <p>QuivixCareers | QuivixDigital.com</p>
            </div>
        </div>
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
