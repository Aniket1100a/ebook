from django.core.management.base import BaseCommand
from core.models import Product

class Command(BaseCommand):
    help = 'Assign default genres to books with no genre'

    def handle(self, *args, **kwargs):
        books_without_genre = Product.objects.filter(genre__isnull=True)
        for book in books_without_genre:
            book.genre = 'Business'  # Assign the correct genre
            book.save()
            self.stdout.write(f"Updated book: {book.title} (ID: {book.id})")

        self.stdout.write("Genre update completed.")
