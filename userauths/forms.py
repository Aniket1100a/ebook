from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User
from django.core.exceptions import ValidationError

# User registration form
class UserRegisterForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "class": "form-control"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm Password", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    # Custom email validation to prevent duplicate email registration
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use. Please use a different email.")
        return email

# User profile form
class UserProfileForm(forms.ModelForm):
    # Adding custom placeholder styling for consistency
    username = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Username", "class": "form-control"})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "Email", "class": "form-control"})
    )
    first_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "First Name", "class": "form-control"})
    )
    last_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Last Name", "class": "form-control"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
