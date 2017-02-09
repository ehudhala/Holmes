from arrow import Arrow
from dateutil import tz
from envelopes import Envelope, GMailSMTP

from holmes.config import EMAIL_DESTINATION, GMAIL_PASSWORD, GMAIL_ADDR, LOG_PATH

ISRAEL_TZ = tz.gettz('Asia/Jerusalem')


def holmes_place_now():
    """
    Returns now in Israel TZ.
    This is the Timezone Holmes Place uses.
    """
    return Arrow.now(tzinfo=ISRAEL_TZ)


def readable_time(time):
    """
    A util function that returns a readable formatting for a time.
    """
    return time.strftime('%d/%m/%y %H:%M')


def send_mail(subject, content, to_addr=EMAIL_DESTINATION, gmail_addr=GMAIL_ADDR, gmail_password=GMAIL_PASSWORD):
    """
    Sends an email.
    :param subject: The subject of the email.
    :param content: The content of the email.
    :param to_addr: The address to send the email to.
    :param gmail_addr: The address to sell the email from (must be gmail).
    :param gmail_password: The password to the gmail account.
    """
    envelope = Envelope(
        from_addr=gmail_addr,
        to_addr=to_addr,
        subject=subject,
        text_body=content
    )

    gmail = GMailSMTP(gmail_addr, gmail_password)
    gmail.send(envelope)


class HolmesPlaceException(Exception):
    """
    All special exceptions raised in this program will subclass this.
    """
    pass


class CouldNotGetActivitiesError(HolmesPlaceException):
    """
    Raised when we can't get activities.
    """
    pass


class CouldNotRegisterError(HolmesPlaceException):
    """
    Raised when we can't register.
    """
    pass


class AuthenticationError(HolmesPlaceException):
    """
    Raised when there was a problem authenticating.
    """
    pass

