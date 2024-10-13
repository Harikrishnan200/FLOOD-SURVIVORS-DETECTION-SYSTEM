from django.shortcuts import render

# Create your views here.
def userLogin(request):
    return render(request, 'Login.html')

def userRegister(request):
    return render(request, 'CreateAccount.html')