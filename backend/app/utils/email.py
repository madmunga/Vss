import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.config import settings


async def send_email(to: str, subject: str, html_body: str) -> None:
    if not settings.SMTP_HOST:
        # In dev / unconfigured environments, just print instead of failing
        print(f"[EMAIL STUB] To={to} Subject={subject}")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER or None,
        password=settings.SMTP_PASSWORD or None,
        start_tls=settings.SMTP_TLS,
    )


async def send_verification_email(to: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    await send_email(
        to=to,
        subject="Verify your VSS account",
        html_body=f"""
        <p>Welcome to <strong>VSS — Veil Support</strong>.</p>
        <p>Please verify your email address by clicking the link below.
           This link expires in 48 hours.</p>
        <p><a href="{link}">{link}</a></p>
        <p>If you did not create an account, you can safely ignore this email.</p>
        """,
    )


async def send_password_reset_email(to: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    await send_email(
        to=to,
        subject="Reset your VSS password",
        html_body=f"""
        <p>We received a request to reset your <strong>VSS</strong> password.</p>
        <p>Click the link below to set a new password. This link expires in 2 hours.</p>
        <p><a href="{link}">{link}</a></p>
        <p>If you did not request a password reset, please ignore this email.</p>
        """,
    )
