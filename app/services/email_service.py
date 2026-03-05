import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

load_dotenv()


def _get_smtp_config() -> dict:
    return {
        "hostname": os.getenv("EMAIL_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("EMAIL_PORT", 587)),
        "username": os.getenv("EMAIL_USERNAME"),
        "password": os.getenv("EMAIL_PASSWORD"),
        "start_tls": True,
    }


def _build_message(to: str, subject: str, salutation: str, body: str, from_: str) -> MIMEMultipart:
    msg = MIMEMultipart()
    msg["From"] = from_
    msg["To"] = to
    msg["Subject"] = subject
    full_body = f"{salutation}\n\n{body}"
    msg.attach(MIMEText(full_body, "plain"))
    return msg


async def send_single_email(to: str, subject: str, salutation: str, body: str) -> None:
    config = _get_smtp_config()
    from_ = os.getenv("EMAIL_FROM", config["username"])
    msg = _build_message(to, subject, salutation, body, from_)
    await aiosmtplib.send(msg, **config)
