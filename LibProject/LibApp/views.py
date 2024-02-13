from django.contrib.auth.views import LoginView, PasswordResetView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.contrib.messages import error
from .forms import SignupForm
from django.contrib.auth import login, authenticate

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