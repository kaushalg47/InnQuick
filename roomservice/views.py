from django.shortcuts import render

def home(request):
    return render(request, 'Home.html')  # Replace 'home.html' with your template name
