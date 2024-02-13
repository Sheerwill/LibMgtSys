from django.urls import path, include
from django.contrib.auth.views import LoginView
from .views import lib_dashboard_view, CustomPasswordResetView, signup

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('library/', lib_dashboard_view, name='lib_dashboard'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),    
    path('accounts/', include('django.contrib.auth.urls')), 
    path('signup/', signup, name='signup'),
]