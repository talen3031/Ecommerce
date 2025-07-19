import os
import resend
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# 初始化 Resend
resend.api_key = os.getenv("RESEND_API_KEY")  # 建議放 .env
#只能寄自己==
def send_email_resend(to_email, subject, html_content):
    response = resend.Emails.send({
        "from": "Nerd.com <Nerd@resend.dev>",  # 這不用驗證
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    })
    return response

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY") 

def send_email(to_email, subject, html_content):
    message = Mail(
        from_email=os.getenv("LINEBOT_ADMIN_EMAIL"),  # 必須要在 SendGrid 後台認證過
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print("SendGrid response:", response.status_code)
    return response
