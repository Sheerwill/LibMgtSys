from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . models import Purchases, Book, Member, Transaction

class SignupForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PurchasesForm(forms.ModelForm):
    class Meta:
        model = Purchases
        fields = ['title', 'author', 'isbn', 'quantity_purchased']

class BooksForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'quantity_available', 'quantity_total']

class MembersForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['name', 'email', 'member_id']

class TransactionsForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['book', 'member', 'transaction_type', 'fee_charged', 'amount_paid']