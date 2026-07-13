import os
from functools import lru_cache
import boto3


@lru_cache(maxsize=1)
def get_ses_client():
    """
    Get a cached instance of the AWS SES client.
    """
    return boto3.client(
        "ses",
        region_name=os.environ["AWS_REGION"],
    )


def send_overdue_reminder(to, book_title, due_date):
    """
    Send an overdue reminder email using AWS SES.
    """
    get_ses_client().send_email(
        Source=os.environ["FROM_EMAIL"],
        Destination={"ToAddresses": [to]},
        Message={
            "Subject": {"Data": f"Overdue: {book_title}"},
            "Body": {
                "Text": {
                    "Data": (
                        f"Your book '{book_title}' was due on "
                        f"{due_date}. Please return it."
                    )
                }
            },
        },
    )
