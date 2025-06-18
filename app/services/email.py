from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from app.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=False,
)

async def send_verification_email(email: EmailStr, token: str):
    verification_link = f"http://localhost:8000/api/auth/verify?token={token}"
    message = MessageSchema(
        subject="Email verification",
        recipients=[email],
        body=f"Hi!\n\nPlease click the link below to verify your email address:\n{verification_link}",
        subtype="plain"
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        print(f"[DEV] Could not send email, verification link: {verification_link}\nError: {e}")