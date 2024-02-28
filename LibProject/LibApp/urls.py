from django.urls import path, include
from django.contrib.auth.views import LoginView
from .views import (lib_dashboard_view, CustomPasswordResetView,
                     signup, newbook, search_book, search_for_book, edit_book,
                     delete_book, newmember, search_for_member, search_member,
                      delete_member, edit_member, newtransaction, search_transaction,
                      search_for_transaction, delete_transaction)

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('library/', lib_dashboard_view, name='lib_dashboard'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),    
    path('accounts/', include('django.contrib.auth.urls')), 
    path('signup/', signup, name='signup'),
    path('newbook/', newbook, name='newbook'),
    path('searchbook/', search_book, name='searchbook'),
    path('search_for_book/', search_for_book, name='search_for_book'),
    path('edit_book/<int:book_id>/', edit_book, name='edit_book'),
    path('delete_book/<int:book_id>/', delete_book, name='delete_book'),
    path('newmember/', newmember, name='newmember'),
    path('searchmember/', search_member, name='searchmember'),
    path('search_for_member/', search_for_member, name='search_for_member'),
    path('edit_member/<int:member_id>/', edit_member, name='edit_member'),
    path('delete_member/<int:member_id>/', delete_member, name='delete_member'),
    path('newtransaction/', newtransaction, name='newtransaction'),
    path('searchtransaction/', search_transaction, name='searchtransaction'),
    path('search_for_transaction/', search_for_transaction, name='search_for_transaction'),
    path('delete_transaction/<int:pk>/', delete_transaction, name='delete_transaction'),
]