from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from .models import Transaction, Book, Member, Purchases

# Create your tests here.
class TransactionModelTests(TestCase):
    def setUp(self):
        self.book = Book.objects.create(title='Test Book', author='Test Author', isbn='1234567890123', quantity_available=5, quantity_total=5)
        self.member = Member.objects.create(name='Test Member', email='test@example.com', member_id='1234', outstanding_debt=0)
    
    def test_transaction_creation(self):
        transaction = Transaction.objects.create(book=self.book, member=self.member, transaction_type='issue', fee_charged=10, amount_paid=5)
        self.assertEqual(transaction.book, self.book)
        self.assertEqual(transaction.member, self.member)
        self.assertEqual(transaction.transaction_type, 'issue')
        self.assertEqual(transaction.fee_charged, 10)
        self.assertEqual(transaction.amount_paid, 5)

    def test_transaction_validation(self):
        # Test that transaction cannot be saved if outstanding debt exceeds 500
        self.member.outstanding_debt = 500
        self.member.save()
        with self.assertRaises(ValidationError):
            Transaction.objects.create(book=self.book, member=self.member, transaction_type='issue', fee_charged=10, amount_paid=1)

        # Test that transaction cannot be saved if quantity available is 0
        self.book.quantity_available = 0
        self.book.save()
        with self.assertRaises(ValidationError):
            Transaction.objects.create(book=self.book, member=self.member, transaction_type='issue', fee_charged=10, amount_paid=1)

    def test_transaction_signals(self):
        # Test that signals are triggered correctly when a transaction is saved
        transaction = Transaction.objects.create(book=self.book, member=self.member, transaction_type='issue', fee_charged=10, amount_paid=5)
        self.assertEqual(self.member.outstanding_debt, 5)
        self.assertEqual(self.book.quantity_available, 4)

class BookTestCase(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            quantity_available=5,
            quantity_total=10
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, "Test Author")
        self.assertEqual(self.book.isbn, "1234567890123")
        self.assertEqual(self.book.quantity_available, 5)
        self.assertEqual(self.book.quantity_total, 10)

    def test_str_representation(self):
        self.assertEqual(str(self.book), "Test Book by Test Author")

    def test_unique_isbn(self):
        # Attempt to create another book with the same ISBN
        with self.assertRaises(Exception):
            Book.objects.create(
                title="Another Book",
                author="Another Author",
                isbn="1234567890123",  # Same ISBN as the first book
                quantity_available=3,
                quantity_total=8
            )

    def test_default_values(self):
        book = Book.objects.create(
            title="Default Book",
            author="Default Author",
            isbn="9876543210987"
        )
        self.assertEqual(book.quantity_available, 0)
        self.assertEqual(book.quantity_total, 0)

class PurchasesTestCase(TestCase):
    def setUp(self):
        # Set up a Book instance for use in testing Purchases
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            quantity_available=5,
            quantity_total=10
        )

    def test_purchases_creation(self):
        # Test creation of Purchases instance
        purchases = Purchases.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            quantity_purchased=3,
        )
        self.assertEqual(purchases.title, "Test Book")
        self.assertEqual(purchases.author, "Test Author")
        self.assertEqual(purchases.isbn, "1234567890123")
        self.assertEqual(purchases.quantity_purchased, 3)    
    
    def test_total_quantity_available_update(self):
        # Test update of total quantity available in Book after purchase
        initial_quantity_available = self.book.quantity_available
        purchases = Purchases.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            quantity_purchased=3,
        )
        updated_book = Book.objects.get(pk=self.book.pk)
        self.assertEqual(updated_book.quantity_available, initial_quantity_available + 3)

    def test_str_representation(self):
        # Test string representation of Purchases instance
        purchases = Purchases.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890123",
            quantity_purchased=3,
        )
        expected_str = f"Purchase of 3 Test Book by Test Author on {purchases.date}"
        self.assertEqual(str(purchases), expected_str)

class MemberModelTests(TestCase):
    def test_valid_member_creation(self):
        # Test creating a valid member
        member = Member.objects.create(
            name="John Doe",
            email="john@example.com",
            member_id="1234",
            outstanding_debt=0
        )
        self.assertEqual(Member.objects.count(), 1)
        self.assertEqual(member.name, "John Doe")
        self.assertEqual(member.email, "john@example.com")
        self.assertEqual(member.member_id, "1234")
        self.assertEqual(member.outstanding_debt, 0)

    # Test invalid email format
    def test_email_field_validation(self):
        invalid_emails = ['test', 'test@', '@example.com']
        for email in invalid_emails:
            member = Member(name='Test Member', email=email, member_id='1234567890')
            with self.assertRaises(ValidationError):
                member.full_clean()
                member.save()

    #Test similar member_id
    def test_unique_member_id_constraint(self):
        member1 = Member.objects.create(name='Test Member 1', email='test1@example.com', member_id='12345')
        member2 = Member(name='Test Member 2', email='test2@example.com', member_id='12345')  # Same ID
        with self.assertRaises(IntegrityError):
            member2.save()