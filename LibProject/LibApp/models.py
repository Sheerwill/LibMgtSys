from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
# The library stock is taken, purchase of books to be handled by accountant not librarian
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)    
    isbn = models.CharField(max_length=13, unique=True)  # Assuming ISBN-13 format      
    quantity_available = models.PositiveIntegerField(default=0)
    quantity_total = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} by {self.author}"

class Purchases(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)    
    isbn = models.CharField(max_length=13)
    quantity_purchased = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now=True)

    def __str__(self):
        return f"Purchase of {self.quantity_purchased} {self.title} by {self.author} on {self.date}"

    def save(self, *args, **kwargs):
        # Check if a book with the provided ISBN exists
        existing_book = Book.objects.filter(isbn=self.isbn).first()

        if existing_book:
            # If the book exists, update its quantity_available and quantity_total
            existing_book.quantity_available += self.quantity_purchased
            existing_book.quantity_total += self.quantity_purchased
            existing_book.save()
        else:
            # If the book doesn't exist, create a new Book instance
            new_book = Book.objects.create(
                title=self.title,
                author=self.author,
                isbn=self.isbn,
                quantity_available=self.quantity_purchased,
                quantity_total=self.quantity_purchased
            )
            new_book.save()

        super().save(*args, **kwargs)
    
class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    member_id = models.CharField(max_length=10, unique=True)
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} - {self.member_id}"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('issue', 'Issue'),
        ('return', 'Return'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    transaction_date = models.DateTimeField(auto_now_add=True)
    fee_charged = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def clean(self):
        super().clean()
        if self.transaction_type == 'return':
            member_outstanding_debt = self.member.outstanding_debt
            new_outstanding_debt = member_outstanding_debt + (self.fee_charged - self.amount_paid)
            if new_outstanding_debt > 500:
                raise ValidationError(f"Member's outstanding debt cannot exceed KES 500.")

    def save(self, *args, **kwargs):
        # Update quantity_available when issuing or returning a book
        if self.transaction_type == 'issue':
            self.book.quantity_available -= 1
            self.book.save()
        elif self.transaction_type == 'return':
            self.book.quantity_available += 1
            self.book.save()
        # Call clean method before saving
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.book.title} - {self.member.name}"
    

