from django.shortcuts import render

# Create your views here.

def rescue_dashboard(request):
    return render(request, 'RescueDashboard.html')