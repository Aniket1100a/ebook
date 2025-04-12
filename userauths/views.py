#userauth/views.py
from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm, UserProfileForm
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import logout
# from django.contrib.auth.models import User  # Ensure you're importing User model correctly.
from userauths.models import User  # Import your custom User model
from django.contrib.auth.decorators import login_required


# If you're using a custom user model, make sure it's referenced properly




def sign_up(request):
    """
    Handles user registration.
    """
    # Redirect authenticated users to the home page (or any other page)
    if request.user.is_authenticated:
        return redirect('core:index')  # Redirect to home page if the user is already logged in

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, your account has been created successfully.")
            
            # Authenticate the user after creation
            new_user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password1'])
            if new_user is not None:
                login(request, new_user)
                return redirect("core:index")  # Redirect to the home page after successful login
        else:
            # If form is not valid, show error messages (e.g., email already in use)
            messages.warning(request, "Please correct the errors in the form.")
    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }

    return render(request, 'userauths/sign_up.html', context)



def sign_in(request):
    # Redirect authenticated users to the home page (or any other page)
    if request.user.is_authenticated:
        messages.warning(request, "Hey, you are already logged in.")
        return redirect('core:index')  # Change to the name of the page you want users to go to

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        try:
            # Fetch the user using your custom User model
            user = User.objects.get(email=email)
            
            # Authenticate the user
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                # Login the user
                login(request, user)
                messages.success(request, "You have logged in successfully!")  # Success message after login
                return redirect('core:index')  # Redirect to some page after successful login
            else:
                # Handle invalid login
                messages.warning(request, "Invalid credentials. Please try again.")  # Error message for invalid login
                return render(request, 'userauths/sign_in.html')
        except User.DoesNotExist:
            # Handle case when user does not exist
            messages.warning(request, "User not found. Please check your email.")  # Error message if user is not found
            return render(request, 'userauths/sign_in.html')
    
    return render(request, 'userauths/sign_in.html')


def sign_out(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("userauths:sign-in")  # Redirect to the homepage or any other page


@login_required
def profile_view(request):
    """
    Handles user profile display.
    """
    return render(request, 'userauths/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('userauths:profile')  # Redirect back to the profile page after saving
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'userauths/edit_profile.html', {'form': form})