from django.urls import path, include
from django.contrib.auth.views import LoginView
from .views import (lib_dashboard_view, CustomPasswordResetView,
                     signup, newbook, search_book, search_for_book, edit_book,
                     delete_book)

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
]