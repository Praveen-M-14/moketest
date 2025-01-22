from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label='Username (Email)', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class CustomUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email.endswith('@sastra.ac.in'):
            raise forms.ValidationError("Email must end with @sastra.ac.in")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Set username as email automatically
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user
