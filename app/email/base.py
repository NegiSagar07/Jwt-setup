from abc import ABC, abstractmethod


class EmailSender(ABC):
    """Provider-agnostic email sender interface.

    Add a new backend (e.g. SES) by implementing this interface in its
    own module and registering it in get_email_sender() below — nothing
    that calls send_password_reset_otp_email() needs to change.
    """

    @abstractmethod
    async def send(self, to_email: str, subject: str, body: str) -> None:
        ...
