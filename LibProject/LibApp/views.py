from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.messages import error
from .forms import SignupForm, PurchasesForm, BooksForm, MembersForm, TransactionsForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from . models import Purchases, Book, Member, Transaction
import json
from django.core.exceptions import ValidationError

# Create your views here.
class CustomLoginView(LoginView):
    def form_valid(self, form):
        # Call the parent class's form_valid method
        super().form_valid(form)
        
        # Redirect to staff dashboard
        return redirect('library')  
    
@login_required
def lib_dashboard_view(request):    
    return render(request, 'lib_dashboard.html')

class CustomPasswordResetView(PasswordResetView):
    email_template_name = 'registration/password_reset_email.html'    
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):        
        email = form.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            # Email doesn't exist in the database
            error(self.request, 'This email is not registered.')
            return self.render_to_response(
                self.get_context_data(form=form, unregistered_email=True)
            )
        return super().form_valid(form)
    
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('lib_dashboard')  
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

def newbook(request):
    if request.method == 'POST':
        form = PurchasesForm(request.POST)
        if form.is_valid():
            form.save() 
            return JsonResponse({'success': True})
        else:
            # Form is not valid, return 'false'
            return JsonResponse({'success': False})
    else:
        form = PurchasesForm()

    return render(request, 'newbook.html', {'form': form})

def search_book(request):
    return render(request, 'searchbook.html')

def search_for_book(request):
    if request.method == 'POST':
        # Get the data from the request body
        data = json.loads(request.body.decode("utf-8"))
        search_query = data.get('q', '')
        search_field = data.get('field', 'title')

        # Determine the field to search based on the selected option
        if search_field == 'title':
            search_results = Book.objects.filter(title__icontains=search_query)
        elif search_field == 'author':
            search_results = Book.objects.filter(author__icontains=search_query)
        elif search_field == 'isbn':
            search_results = Book.objects.filter(isbn__icontains=search_query)
        else:
            # If the selected field is not recognized, return an empty queryset
            search_results = Book.objects.none()

        # Serialize the search results
        serialized_results = [{'id': book.id, 'title': book.title, 'author': book.author,
                                'isbn': book.isbn, 'quantity_available': book.quantity_available,
                                } for book in search_results]

        return JsonResponse({'results': serialized_results})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def edit_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if request.method == 'POST':
        form = BooksForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            # Redirect to a success page or do something else
    else:
        form = BooksForm(instance=book)
    
    return render(request, 'editbook.html', {'form': form})

def delete_book(request, book_id):
    # Get the book object
    book = get_object_or_404(Book, pk=book_id)
    
    # Delete the book
    book.delete()
    
    # Return a success response
    return JsonResponse({'success': True})

def newmember(request):
    if request.method == 'POST':
        form = MembersForm(request.POST)
        if form.is_valid():
            form.save() 
            return JsonResponse({'success': True})
        else:
            # Form is not valid, return 'false'
            return JsonResponse({'success': False})
    else:
        form = MembersForm()

    return render(request, 'newmember.html', {'form': form})

def search_member(request):
    return render(request, 'searchmember.html')

def search_for_member(request):
    if request.method == 'POST':
        # Get the data from the request body
        data = json.loads(request.body.decode("utf-8"))
        search_query = data.get('q', '')
        search_field = data.get('field', 'name')

        # Determine the field to search based on the selected option
        if search_field == 'name':
            search_results = Member.objects.filter(name__icontains=search_query)
        elif search_field == 'email':
            search_results = Member.objects.filter(email__icontains=search_query)
        elif search_field == 'member_id':
            search_results = Member.objects.filter(member_id__icontains=search_query)
        else:
            # If the selected field is not recognized, return an empty queryset
            search_results = Member.objects.none()

        # Serialize the search results
        serialized_results = [{'id': member.id, 'name': member.name, 'email': member.email, 'member_id': member.member_id, 'debt': member.outstanding_debt} for member in search_results]

        return JsonResponse({'results': serialized_results})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def edit_member(request, member_id):
    member = get_object_or_404(Member, pk=member_id)
    
    if request.method == 'POST':
        form = MembersForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            # Redirect to a success page or do something else
    else:
        form = MembersForm(instance=member)
    
    return render(request, 'editmember.html', {'form': form})

def delete_member(request, member_id):
    # Get the book object
    member = get_object_or_404(Member, pk=member_id)
    
    # Delete the book
    member.delete()
    
    # Return a success response
    return JsonResponse({'success': True})

def newtransaction(request):
    if request.method == 'POST':
        form = TransactionsForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return JsonResponse({'success': True})
            except ValidationError as e:
                return JsonResponse({'success': False, 'error_message': str(e)})
        else:
            # Form is not valid, return 'false'
            return JsonResponse({'success': False})
    else:
        form = TransactionsForm()

    return render(request, 'newtransaction.html', {'form': form})

def search_transaction(request):
    return render(request, 'searchtransaction.html')

def search_for_transaction(request):
    if request.method == 'POST':
        # Get the data from the request body
        data = json.loads(request.body.decode("utf-8"))
        search_query = data.get('q', '')
        search_field = data.get('field', 'book')

        # Initialize search results variable
        search_results = []

        # Determine the field to search based on the selected option
        if search_field == 'book':
            search_results = Transaction.objects.filter(book__isbn__icontains=search_query)
        elif search_field == 'member':
            search_results = Transaction.objects.filter(member__member_id__icontains=search_query)
        elif search_field == 'transaction_type':
            search_results = Transaction.objects.filter(transaction_type__icontains=search_query)
        else:
            # If the selected field is not recognized, return an empty list
            pass

        # Serialize the search results
        serialized_results = []
        for result in search_results:
            serialized_results.append({
                'id': result.id,
                'book_title': result.book.title,
                'member_name': result.member.name,
                'transaction_type': result.transaction_type,
                'transaction_date': result.transaction_date.strftime("%Y-%m-%d %H:%M:%S"),
                'fee_charged': str(result.fee_charged),
                'amount_paid': str(result.amount_paid)
            })

        return JsonResponse({'results': serialized_results})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
def delete_transaction(request, pk):
    # Get the transaction object
    transaction = get_object_or_404(Transaction, pk=pk)
    
    # Delete the transaction
    transaction.delete()
    
    # Return a success response
    return JsonResponse({'success': True})

def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    
    if request.method == 'POST':
        form = TransactionsForm(request.POST, instance=transaction)
        if form.is_valid():
            # Save the form to get the updated transaction data
            updated_transaction = form.save(commit=False)
            
            # Calculate the change in outstanding debt
            original_outstanding_debt = updated_transaction.member.outstanding_debt         
            
            # Update the outstanding debt
            updated_transaction.member.outstanding_debt = original_outstanding_debt - updated_transaction.amount_paid            
            updated_transaction.member.save()

            # Save the updated transaction
            updated_transaction.save()    
        
    else:
        form = TransactionsForm(instance=transaction)
    
    return render(request, 'edittransaction.html', {'form': form})