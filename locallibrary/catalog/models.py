import uuid
from datetime import date

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse


class Genre(models.Model):
    """Model representing the book genre."""

    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry, etc.)",
    )

    def __str__(self):
        """String for representing the Genre object"""
        return self.name

    def get_absolute_url(self):
        return reverse("genre-detail", args=[str(self.id)])

    class Meta:
        constraints = [  # noqa: RUF012
            UniqueConstraint(
                Lower("name"),
                name="genre_name_case_insensitive_unique",
                violation_error_message="Genre already exists (case-insensitive match)",
            )
        ]


class Book(models.Model):
    """Model representing a book."""

    title = models.CharField(max_length=200)
    author = models.ForeignKey("Author", on_delete=models.RESTRICT, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book."
    )
    isbn = models.CharField(
        verbose_name="ISBN",
        max_length=13,
        unique=True,
        help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn'
        '">ISBN number</a>',
    )

    # Relationships
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book.")
    language = models.ForeignKey("Language", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book-detail", args=[str(self.id)])

    def display_genre(self):
        """Create string for the genre. This is required to display genre in the Django admin interface"""
        return ", ".join(genre.name for genre in self.genre.all()[:3])


class BookInstance(models.Model):
    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    """Model representing an individual book"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Unique ID for this particular book.",
    )
    due_back = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default="m",
        help_text="Book availability",
    )
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200, blank=True, null=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    class Meta:
        ordering = ["due_back"]  # noqa: RUF012
        permissions = (("can_mark_returned", "Set book as returned"),)

    def __str__(self):
        """String for representing the BookInstance object."""
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(verbose_name="died", null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]  # noqa: RUF012

    def get_absolute_url(self):
        return reverse("author-detail", args=[str(self.id)])

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"


class Language(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)",
    )

    def get_absolute_url(self):
        return reverse("language_detail", args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        constraints = [  # noqa: RUF012
            UniqueConstraint(
                Lower("name"),
                name="language_name_case_insensitive_unique",
                violation_error_message="Language already exists (case insensitive match)",
            )
        ]
