from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Replace 'home.html' with your template name
