import os
from functools import lru_cache
from azure.communication.email import EmailClient


@lru_cache(maxsize=1)
def get_email_client():
    """
    Get a cached instance of the Azure Email client.
    """
    return EmailClient.from_connection_string(
        os.environ["AZURE_COMM_CONNECTION_STRING"]
    )


def send_overdue_reminder(to, book_title, due_date):
    """
    Send an overdue reminder email using Azure Communication Services.
    """
    message = (
        f"Your book '{book_title}' was due on {due_date}. "
        f"Please return it."
    )
    get_email_client().begin_send(
        senderAddress=os.environ["FROM_EMAIL"],
        recipients={"to": [{"address": to}]},
        content={
            "subject": f"Overdue: {book_title}",
            "plain_text": message,
        },
    ).result()
