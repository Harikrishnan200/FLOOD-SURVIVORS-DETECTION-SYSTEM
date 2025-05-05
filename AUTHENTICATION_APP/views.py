from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            if user.is_admin and not user.is_super_admin:
                return redirect('dashboard')  
            elif user.role == 'volunteer':
                return redirect('volunteer_dashboard')
            elif user.is_super_admin:
                return redirect('super_admin_dashboard')
            else:
                return redirect('rescue_dashboard') 
        else:
            messages.error(request, "Invalid email or password.")
    return render(request, 'Login.html')




def user_register(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        country = request.POST.get('country')
        role = request.POST.get('role')
        print("Role: ", role)

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('register')

        try:
            user = CustomUser.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password1,
                country=country,
                role=role
            )
            messages.success(request, "Registration successful. You can now log in.")
            print("Registration successful. You can now log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('register')

    return render(request, 'Register.html')


@login_required(login_url='login')
def user_logout(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('login')  


@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html', {'user': request.user})

@login_required(login_url='login')
def adminDashboard(request):
    return render(request, 'AdminDashboard.html')

@login_required(login_url='login')
def userDashboard(request):
    return render(request, 'RescueDashboard.html')


