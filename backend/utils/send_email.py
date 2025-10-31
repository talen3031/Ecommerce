import os
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from flask import current_app

# def send_email_resend(to_email, subject, html_content):
#     # 盡量用 current_app 拿 config，沒有就 fallback config["default"]
#     try:
#         api_key = current_app.config["RESEND_API_KEY"]
#     except RuntimeError:
#         from config import config
#         api_key = config["default"].RESEND_API_KEY
#     resend.api_key = api_key

#     response = resend.Emails.send({
#         "from": "Raw type <Nerd@resend.dev>",
#         "to": [to_email],
#         "subject": subject,
#         "html": html_content,
#     })
#     return response

def send_email(to_email, subject, html_content):
    try:
        sendgrid_api_key = current_app.config["SENDGRID_API_KEY"]
        from_email = current_app.config["LINEBOT_ADMIN_EMAIL"]
    except RuntimeError:
        from config import config
        sendgrid_api_key = config["default"].SENDGRID_API_KEY
        from_email = config["default"].LINEBOT_ADMIN_EMAIL

    message = Mail(
        from_email=from_email,  # SendGrid 後台必須認證過
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    sg = SendGridAPIClient(sendgrid_api_key)
    response = sg.send(message)
    print("SendGrid response:", response.status_code)
    return response