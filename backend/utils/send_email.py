import os
import resend

# 初始化 Resend
resend.api_key = os.getenv("RESEND_API_KEY")  # 建議放 .env

def send_email(to_email, subject, html_content):
    response = resend.Emails.send({
        "from": "Nerd.com <Nerd@resend.dev>",  # 這不用驗證
        "to": [to_email],
        "subject": subject,
        "html": html_content,
    })
    return response
