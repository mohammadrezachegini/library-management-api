from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Book
from notifications.sender import send_overdue_reminder


class Command(BaseCommand):
    help = "send overdue book reminders via email"

    def handle(self, *args, **kwargs):
        overdue_books = Book.objects.filter(status="borrowed")

        if not overdue_books.exists():
            self.stdout.write("No overdue books found.")
            return

        for book in overdue_books:
            send_overdue_reminder(
                to="reza.dev.1994@gmail.com",
                book_title=book.title,
                due_date=str(timezone.now().date()),
            )
            self.stdout.write(f"Reminder sent for book: {book.title}")
