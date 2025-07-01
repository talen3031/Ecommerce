import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


SENDGRID_API_KEY = "SENDGRID_API_KEY"  
#SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")  # 建議放環境變數
FROM_EMAIL = "your email"                 # 必須是SendGrid已認證的email

def send_email(to_email, subject, html_content):
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=to_email,
        subject=subject,
        html_content=html_content
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Email sent! status_code={response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"SendGrid error: {e}")
        return None
