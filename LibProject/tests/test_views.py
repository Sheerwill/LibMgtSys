from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from LibApp.models import Book, Member, Transaction, Purchases
from LibApp.forms import TransactionsForm
import json
from decimal import Decimal

class CustomLoginViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_custom_login_view_redirects_to_staff_dashboard(self):
        # Log in the user
        self.client.login(username='testuser', password='password')
        
        # Make a POST request to the login view
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': 'password'})
        
        # Check if the response is a redirect
        self.assertEqual(response.status_code, 302)
        
        # Check if the redirect leads to the library dashboard
        self.assertEqual(response.url, reverse('lib_dashboard'))

class LibDashboardViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_redirect_when_not_logged_in(self):
        # Make a GET request to the library dashboard view
        response = self.client.get(reverse('lib_dashboard'))
        
        # Check if the response status code is 302 (redirect)
        self.assertEqual(response.status_code, 302)
        
        # Check if the response redirects to the login page
        self.assertRedirects(response, '/accounts/login/?next=/library/')

class CustomPasswordResetViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_password_reset_form_rendered(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')

    def test_password_reset_form_submission_valid_email(self):
        # Create a user with a valid email
        user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        
        # Make a POST request to the password reset view with a valid email
        response = self.client.post(reverse('password_reset'), {'email': 'test@example.com'})
        
        # Check if the email was sent successfully
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('test@example.com', mail.outbox[0].to)

    def test_password_reset_form_submission_invalid_email(self):
        # Make a POST request to the password reset view with an invalid email
        response = self.client.post(reverse('password_reset'), {'email': 'invalid@example.com'})
        
        # Check if the response renders the form again with an error message
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')
        self.assertIn(b'The provided email address is not registered.', response.content)

class NewBookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_newbook_view_rendered(self):
        response = self.client.get(reverse('newbook'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newbook.html')

    def test_newbook_form_submission_valid(self):
        data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '1234567890123',
            'quantity_purchased': 10,
        }
        response = self.client.post(reverse('newbook'), data)
        
        # Check if the response contains a JSON success message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)

        # Check if the book was saved to the database
        self.assertTrue(Book.objects.filter(title='Test Book').exists())

    def test_newbook_form_submission_invalid(self):
        # Missing required fields
        data = {}
        response = self.client.post(reverse('newbook'), data)
        
        # Check if the response contains a JSON failure message
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)

        # Check if the book was not saved to the database
        self.assertFalse(Book.objects.exists())

class SearchBookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_book_view_rendered(self):
        response = self.client.get(reverse('searchbook'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'searchbook.html')

class SearchForBookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.book1 = Book.objects.create(title='Book1', author='Author1', isbn='1234567890123', quantity_available=5)
        self.book2 = Book.objects.create(title='Book2', author='Author2', isbn='1234567890124', quantity_available=3)

    def test_search_for_book_post_success(self):
        data = {'q': 'Book1', 'field': 'title'}
        response = self.client.post(reverse('search_for_book'), json.dumps(data), content_type='application/json')
        
        # Check if the response contains the expected JSON data
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['title'], 'Book1')

    def test_search_for_book_post_invalid_field(self):
        data = {'q': 'Author2', 'field': 'invalid_field'}
        response = self.client.post(reverse('search_for_book'), json.dumps(data), content_type='application/json')
        
        # Check if the response contains an empty result set
        self.assertEqual(response.status_code, 200)
        self.assertIn('results', response.json())
        self.assertEqual(len(response.json()['results']), 0)

    def test_search_for_book_get_not_allowed(self):
        response = self.client.get(reverse('search_for_book'))
        
        # Check if the response contains the expected error message and status code
        self.assertEqual(response.status_code, 405)
        self.assertIn('error', response.json())
        self.assertEqual(response.json()['error'], 'Method not allowed')

class EditBookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Book1', author='Author1', isbn='1234567890123', quantity_available=5)

    def test_edit_book_view_rendered(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('edit_book', args=[self.book.pk]))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'editbook.html')
        self.assertTrue('form' in response.context)

    def test_edit_book_post_valid_form(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'title': 'Edited Book',
            'author': 'Edited Author',
            'isbn': '1234567890124',
            'quantity_available': 10,
            'quantity_total': 15,  # Including quantity_total in the form data
        }
        response = self.client.post(reverse('edit_book', args=[self.book.pk]), data)
        
        # Check if the book was updated in the database
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Edited Book')
        self.assertEqual(self.book.author, 'Edited Author')
        self.assertEqual(self.book.isbn, '1234567890124')
        self.assertEqual(self.book.quantity_available, 10)
        self.assertEqual(self.book.quantity_total, 15)  # Checking quantity_total update

    def test_edit_book_post_invalid_form(self):
        self.client.login(username='testuser', password='testpassword')
        data = {
            'title': '',  # Invalid: title is empty
            'author': 'Edited Author',
            'isbn': '1234567890124',
            'quantity_available': 10,
            'quantity_total': 15,  # Including quantity_total in the form data
        }
        response = self.client.post(reverse('edit_book', args=[self.book.pk]), data)
        
        # Check if the book was not updated in the database
        self.assertEqual(response.status_code, 200)
        self.book.refresh_from_db()
        self.assertNotEqual(self.book.title, '')  # Title should not be empty after invalid form submission

class DeleteBookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.book = Book.objects.create(title='Book1', author='Author1', isbn='1234567890123', quantity_available=5)

    def test_delete_book_view(self):
        self.client.login(username='testuser', password='testpassword')
        
        # Get the initial count of books
        initial_book_count = Book.objects.count()
        
        # Make a DELETE request to delete the book
        response = self.client.delete(reverse('delete_book', args=[self.book.pk]))
        
        # Check if the book was deleted
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Book.objects.count(), initial_book_count - 1)
        
        # Check if the response indicates success
        self.assertTrue(response.json()['success'])

class SignupViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup_post_valid_form(self):
        # Create a POST request with valid form data
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }
        response = self.client.post(reverse('signup'), data)
        
        # Check if the user was created and redirected to the expected page
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_signup_post_invalid_form(self):
        # Create a POST request with invalid form data (passwords don't match)
        data = {
            'username': 'testuser2',
            'email': 'testuser2@example.com',
            'password1': 'testpassword1',
            'password2': 'testpassword2',  # Passwords don't match
        }
        response = self.client.post(reverse('signup'), data)
        
        # Check if the user was not created and the form was rendered again with errors
        self.assertEqual(response.status_code, 200)  # Expecting a rendered template
        self.assertFalse(User.objects.filter(username='testuser2').exists())

class SearchMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_member_view(self):
        response = self.client.get(reverse('searchmember'))
        
        # Check if the view renders the searchmember.html template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'searchmember.html')

class SearchForMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_for_member_post_valid_query(self):
        # Create a member object for testing
        Member.objects.create(name='John Doe', email='john@example.com', member_id='12345', outstanding_debt=100)

        # Create a POST request with valid search parameters
        data = {
            'q': 'John Doe',  # Searching for member by name
            'field': 'name',   # Searching by name field
        }
        response = self.client.post(reverse('search_for_member'), data, content_type='application/json')
        
        # Check if the response contains the search results
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.json())
        self.assertEqual(len(response.json()['results']), 1)  # Check if exactly one member is returned

    def test_search_for_member_post_invalid_query(self):
        # Create a POST request with invalid search parameters
        data = {
            'q': 'Jane Smith',   # Non-existing member name
            'field': 'name',     # Searching by name field
        }
        response = self.client.post(reverse('search_for_member'), data, content_type='application/json')
        
        # Check if the response indicates no results found
        self.assertEqual(response.status_code, 200)
        self.assertTrue('results' in response.json())
        self.assertEqual(len(response.json()['results']), 0)  # Check if no member is returned

class EditMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(name='John Doe', email='john@example.com', member_id='12345', outstanding_debt=100)

    def test_edit_member_post_valid_form(self):
        # Create a POST request with valid form data
        data = {
            'name': 'Edited Name',
            'email': 'edited@example.com',
            'member_id': '54321',
        }
        response = self.client.post(reverse('edit_member', args=[self.member.pk]), data)
        
        # Check if the member was updated in the database
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()
        self.assertEqual(self.member.name, 'Edited Name')
        self.assertEqual(self.member.email, 'edited@example.com')
        self.assertEqual(self.member.member_id, '54321')
        self.assertEqual(self.member.outstanding_debt, 100)  # Outstanding debt should remain unchanged

    def test_edit_member_post_invalid_form(self):
        # Create a POST request with invalid form data (missing required field)
        data = {
            'name': '',  # Invalid: name is empty
            'email': 'edited@example.com',
            'member_id': '54321',
        }
        response = self.client.post(reverse('edit_member', args=[self.member.pk]), data)
        
        # Check if the member was not updated in the database
        self.assertEqual(response.status_code, 200)
        self.member.refresh_from_db()        
        self.assertNotEqual(self.member.email, 'edited@example.com')  # Email should not be updated with invalid form data

class DeleteMemberViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.member = Member.objects.create(name='Test Member', email='test@example.com', member_id='12345')

    def test_delete_member(self):
        # Log in as the user (if authentication is required)
        self.client.login(username='testuser', password='testpassword')

        # Get the initial count of members
        initial_count = Member.objects.count()

        # Send a DELETE request to delete the member
        response = self.client.delete(reverse('delete_member', args=[self.member.pk]))

        # Check if the member was deleted successfully (HTTP 200 OK response)
        self.assertEqual(response.status_code, 200)

        # Verify that the member no longer exists in the database
        self.assertFalse(Member.objects.filter(pk=self.member.pk).exists())

        # Verify that the count of members has decreased by 1
        self.assertEqual(Member.objects.count(), initial_count - 1)


class NewTransactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a book and a member for testing
        self.book = Purchases.objects.create(
            title='Test Book', 
            author='Test Author', 
            isbn='1234567890123',
            quantity_purchased=1  # Example value for quantity purchased
        )
        self.member = Member.objects.create(
            name='Test Member', 
            email='test@example.com', 
            member_id='123'
        )

    def test_render_newtransaction_form(self):
        # Test rendering the new transaction form
        response = self.client.get(reverse('newtransaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newtransaction.html')
        self.assertIsInstance(response.context['form'], TransactionsForm)

    def test_newtransaction_valid_post(self):
        # Test submitting a valid transaction form
        form_data = {
            'book': self.book.id,
            'member': self.member.id,
            'transaction_type': 'issue',  # Valid transaction type
            'fee_charged': 10.0,
            'amount_paid': 10.0,
        }
        response = self.client.post(reverse('newtransaction'), data=form_data)

        # Check if the transaction was saved successfully
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], True)
        self.assertTrue(Transaction.objects.exists())

    def test_newtransaction_invalid_post(self):
        # Test submitting an invalid transaction form (missing required fields)
        form_data = {}  # No data provided, form will be invalid
        response = self.client.post(reverse('newtransaction'), data=form_data)

        # Check if the response indicates failure and form validation errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)        

    def test_newtransaction_invalid_data_post(self):
        # Test submitting invalid data in the transaction form
        form_data = {
            'book': self.book.id,
            'member': self.member.id,
            'transaction_type': 'InvalidType',  # Invalid transaction type
            'fee_charged': 'invalid_fee',  # Invalid fee format
            'amount_paid': 'invalid_amount',  # Invalid amount format
            # Add other invalid data
        }
        response = self.client.post(reverse('newtransaction'), data=form_data)

        # Check if the response indicates failure and form validation errors
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['success'], False)

class SearchTransactionViewTestCase(TestCase):
    def test_search_transaction_view(self):
        # Make a GET request to the search_transaction view
        response = self.client.get(reverse('searchtransaction'))

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Check if the correct template is used
        self.assertTemplateUsed(response, 'searchtransaction.html')

class SearchForTransactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_search_for_transaction_post(self):
        # Prepare POST data
        post_data = {'q': 'search_query', 'field': 'book'}
        json_data = json.dumps(post_data)

        # Make a POST request to the search_for_transaction view
        response = self.client.post(reverse('search_for_transaction'), data=json_data, content_type='application/json')

        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)

        # Assert the expected keys in the response JSON
        response_data = response.json()
        self.assertIn('results', response_data)

    def test_search_for_transaction_get(self):
        # Make a GET request to the search_for_transaction view
        response = self.client.get(reverse('search_for_transaction'))

        # Check if the response status code is 405 (Method Not Allowed)
        self.assertEqual(response.status_code, 405)   

class DeleteTransactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a book instance
        self.book = Purchases.objects.create(title='Test Book', author='Test Author', isbn='1234567890123', quantity_purchased=5)
        # Create a member instance
        self.member = Member.objects.create(name='Test Member', email='test@example.com', member_id='12345')
        # Create a form instance with valid data
        form_data = {
            'book': self.book.pk,
            'member': self.member.pk,
            'transaction_type': 'issue',
            'fee_charged': 10,
            'amount_paid': 5
        }
        form = TransactionsForm(form_data)
        self.assertTrue(form.is_valid())  # Ensure the form is valid
        # Create the transaction using the form data
        self.transaction = form.save()

    def test_delete_transaction(self):
        # Get the initial count of transactions
        initial_count = Transaction.objects.count()

        # Send a POST request to delete the transaction
        response = self.client.post(reverse('delete_transaction', args=[self.transaction.pk]))

        # Check if the response indicates success
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'success': True})

        # Check if the transaction is deleted
        self.assertEqual(Transaction.objects.count(), initial_count - 1)  

class EditTransactionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a book instance
        self.book = Book.objects.create(title='Test Book', author='Test Author', isbn='1234567890123', quantity_available=5, quantity_total=5)
        # Create a member instance
        self.member = Member.objects.create(name='Test Member', email='test@example.com', member_id='12345')
        # Create a transaction instance
        self.transaction = Transaction.objects.create(book=self.book, member=self.member,
                                                      transaction_type='issue', fee_charged=10, amount_paid=5)        

    def test_edit_transaction(self):
        # Send a GET request to get the edit form
        response = self.client.get(reverse('edit_transaction', args=[self.transaction.pk]))

        # Check if the response status code is 200 and the correct template is used
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edittransaction.html')

        # Get the initial values of the transaction
        #initial_amount_paid = self.transaction.amount_paid
        initial_outstanding_debt = self.member.outstanding_debt        

        # Send a POST request to edit the transaction
        updated_amount_paid = Decimal('5')  # New amount paid
        form_data = {
            'book': self.book.pk,
            'member': self.member.pk,
            'transaction_type': 'return',
            'fee_charged': '10',  # New fee charged            
            'amount_paid': updated_amount_paid
        }
        response = self.client.post(reverse('edit_transaction', args=[self.transaction.pk]), form_data)

        # Check if the response status code is 200 and the transaction is updated
        self.assertEqual(response.status_code, 200)
        self.transaction.refresh_from_db()  # Refresh the transaction instance from the database

        # Check if the transaction data is updated correctly        
        self.assertEqual(self.transaction.amount_paid, updated_amount_paid)

        # Check if the member's outstanding debt is updated correctly
        self.member.refresh_from_db()  # Refresh the member instance from the database
        expected_outstanding_debt = initial_outstanding_debt - updated_amount_paid
        self.assertEqual(self.member.outstanding_debt, expected_outstanding_debt)