from textwrap import dedent

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.mailing.config import email_settings
from src.jinja_templates import templates

async def send_email(
        recepient: str,
        subject: str,
        plain_content: str,
        html_content: str = ""
    ):  
    message = MIMEMultipart("alternative")
    message["From"] = email_settings.email_sender
    message["To"] = recepient
    message["Subject"] = subject

    plain_text_message = MIMEText(
        plain_content, 
        "plain", 
        "utf-8"
    )
    message.attach(plain_text_message)

    if html_content:  
        html_message = MIMEText(
            html_content, 
            "html", 
            "utf-8"
        )
        message.attach(html_message)
    
    await aiosmtplib.send(
        message,
        hostname=email_settings.smtp_host,
        port=email_settings.smtp_port,
        username=email_settings.email_sender,
        password=email_settings.email_passcode
    )

async def send_confirmation_email(
    username: str,
    recipient: str,
    confirmation_link: str
):
    subject = "Confirm your email for site.com"
    plain_text = dedent(f"""
        Hello {username},

Thank you for signing up! Please confirm your email address to activate your account.

Click the link below to verify your email:
{ confirmation_link }

If you didn’t create an account, you can safely ignore this email.
    """)

    template = templates.get_template("confirmation_email.html")
    context = {
        "username": username,
        "confirmation_link": confirmation_link
    }

    html_content = template.render(context)

    await send_email(
        recepient=recipient,
        subject=subject,
        plain_content=plain_text,
        html_content=html_content
    )

async def send_password_reset_email(
        username: str,
        recepient: str,
        password_reset_link: str
):
    subject = "Reset your password on site.com"
    plain_text = dedent(f"""Hello, { username }!

You have requested to reset the password for your account.

To proceed, please click the following link:
{ password_reset_link }
If you did not request a password reset, simply ignore this message."""
)
    template = templates.get_template("password_reset_email.html")
    context = {
        "username": username,
        "password_reset_link": password_reset_link
    }
    html_content = template.render(context)

    await send_email(
        recepient=recepient,
        subject=subject,
        plain_content=plain_text,
        html_content=html_content
    )