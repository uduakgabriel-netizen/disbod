from django.shortcuts import render

def index(request):
    return render(request, 'landing.html')

def signup(request):
    return render(request, 'signup.html')

def login(request):
    return render(request, 'login.html')

def base(request):
    return render(request, 'base.html')
