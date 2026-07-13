import os


def send_overdue_reminder(to, book_title, due_date):
    """
    Send an overdue reminder email using the configured email service.
    """
    provider = os.environ.get("EMAIL_PROVIDER", "local").lower()

    if provider == "aws":
        from .aws_email import send_overdue_reminder as _send
    elif provider == "azure":
        from .azure_email import send_overdue_reminder as _send
    else:
        # Local dev - just print
        print(
            f"Sending email to {to}: Your book '{book_title}' "
            f"was due on {due_date}. Please return it."
        )
        return

    _send(to, book_title, due_date)
