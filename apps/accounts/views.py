"""
Views for the accounts app
"""
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CustomUserCreationForm
from .models import UserProfile


class RegisterView(CreateView):
    """User registration view"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """Display user profile"""
    template_name = 'accounts/profile.html'


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Edit user profile"""
    model = UserProfile
    fields = ['bio', 'website', 'location', 'birth_date']
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileCreateView(LoginRequiredMixin, CreateView):
    """Create user profile"""
    model = UserProfile
    fields = ['bio', 'website', 'location', 'birth_date']
    template_name = 'accounts/profile_form.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
