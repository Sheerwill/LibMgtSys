from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    quantity_total = models.IntegerField(default=0)
    quantity_available = models.IntegerField(default=0)

    def __str__(self):
        return self.title
    
class Member(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
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

    def clean(self):
        super().clean()
        if self.transaction_type == 'return':
            member_outstanding_debt = self.member.outstanding_debt
            new_outstanding_debt = member_outstanding_debt + self.fee_charged
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
    

