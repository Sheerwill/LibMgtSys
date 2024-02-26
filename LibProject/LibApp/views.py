from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.messages import error
from .forms import SignupForm, PurchasesForm, BooksForm, MembersForm
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from . models import Purchases, Book, Member
import json

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
        serialized_results = [{'id': book.id, 'title': book.title, 'author': book.author, 'isbn': book.isbn} for book in search_results]

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
        serialized_results = [{'id': member.id, 'name': member.name, 'email': member.email, 'member_id': member.member_id} for member in search_results]

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