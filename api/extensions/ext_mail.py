import logging
from typing import Optional

import resend
from flask import Flask

from configs import mlchain_config


class Mail:
    def __init__(self):
        self._client = None
        self._default_send_from = None

    def is_inited(self) -> bool:
        return self._client is not None

    def init_app(self, app: Flask):
        mail_type = mlchain_config.MAIL_TYPE
        if not mail_type:
            logging.warning("MAIL_TYPE is not set")
            return

        if mlchain_config.MAIL_DEFAULT_SEND_FROM:
            self._default_send_from = mlchain_config.MAIL_DEFAULT_SEND_FROM

        match mail_type:
            case "resend":
                api_key = mlchain_config.RESEND_API_KEY
                if not api_key:
                    raise ValueError("RESEND_API_KEY is not set")

                api_url = mlchain_config.RESEND_API_URL
                if api_url:
                    resend.api_url = api_url

                resend.api_key = api_key
                self._client = resend.Emails
            case "smtp":
                from libs.smtp import SMTPClient

                if not mlchain_config.SMTP_SERVER or not mlchain_config.SMTP_PORT:
                    raise ValueError("SMTP_SERVER and SMTP_PORT are required for smtp mail type")
                if not mlchain_config.SMTP_USE_TLS and mlchain_config.SMTP_OPPORTUNISTIC_TLS:
                    raise ValueError("SMTP_OPPORTUNISTIC_TLS is not supported without enabling SMTP_USE_TLS")
                self._client = SMTPClient(
                    server=mlchain_config.SMTP_SERVER,
                    port=mlchain_config.SMTP_PORT,
                    username=mlchain_config.SMTP_USERNAME,
                    password=mlchain_config.SMTP_PASSWORD,
                    _from=mlchain_config.MAIL_DEFAULT_SEND_FROM,
                    use_tls=mlchain_config.SMTP_USE_TLS,
                    opportunistic_tls=mlchain_config.SMTP_OPPORTUNISTIC_TLS,
                )
            case _:
                raise ValueError("Unsupported mail type {}".format(mail_type))

    def send(self, to: str, subject: str, html: str, from_: Optional[str] = None):
        if not self._client:
            raise ValueError("Mail client is not initialized")

        if not from_ and self._default_send_from:
            from_ = self._default_send_from

        if not from_:
            raise ValueError("mail from is not set")

        if not to:
            raise ValueError("mail to is not set")

        if not subject:
            raise ValueError("mail subject is not set")

        if not html:
            raise ValueError("mail html is not set")

        self._client.send(
            {
                "from": from_,
                "to": to,
                "subject": subject,
                "html": html,
            }
        )


def init_app(app: Flask):
    mail.init_app(app)


mail = Mail()
